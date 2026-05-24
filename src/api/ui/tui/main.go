package main

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// --- STYLES ---
var (
	baseStyle  = lipgloss.NewStyle().BorderStyle(lipgloss.NormalBorder()).BorderForeground(lipgloss.Color("240"))
	panelStyle = lipgloss.NewStyle().BorderStyle(lipgloss.RoundedBorder()).BorderForeground(lipgloss.Color("#7D56F4")).Padding(1, 2)

	titleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#FAFAFA")).Background(lipgloss.Color("#7D56F4")).Padding(0, 2).MarginBottom(1)

	activeTabStyle   = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#EE6FF8")).Border(lipgloss.NormalBorder(), false, false, true, false).BorderForeground(lipgloss.Color("#EE6FF8")).Padding(0, 2)
	inactiveTabStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("240")).Border(lipgloss.NormalBorder(), false, false, true, false).BorderForeground(lipgloss.Color("240")).Padding(0, 2)

	metricLabelStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("241")).Bold(true)
	metricValueStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#00ADD8")).Bold(true).PaddingLeft(1)
	helpStyle        = lipgloss.NewStyle().Foreground(lipgloss.Color("241")).MarginTop(1)

	onlineStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#04B575")).Bold(true)
	offlineStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#FF4C4C")).Bold(true)
)

// --- MESSAGES & MODELS ---
type tickMsg time.Time

type txLog struct {
	ID     string `json:"id"`
	Amount string `json:"amount"`
	Status string `json:"status"`
}

type metricsResponse struct {
	RPS        uint64  `json:"rps"`
	AvgLatency float64 `json:"avg_latency"`
	Logs       []txLog `json:"logs"`
}

type systemStatus struct {
	api      string
	redis    string
	redpanda string
}

type model struct {
	activeTab int
	tabs      []string

	// Tab 0: Metrics
	logTable    table.Model
	filterInput textinput.Model
	rpsHistory  []float64
	currentRPS  uint64
	avgLatency  float64
	recentLogs  []txLog

	// Tab 1: Health
	health systemStatus

	// Tab 2: Kubernetes
	k8sTable table.Model
}

func initialModel() model {
	// Log Table Setup with Focus enabled
	logCols := []table.Column{
		{Title: "TX ID", Width: 30},
		{Title: "AMOUNT", Width: 15},
		{Title: "STATUS", Width: 15},
	}
	tLog := table.New(
		table.WithColumns(logCols),
		table.WithHeight(7),
		table.WithFocused(true), // FIXED: Enables arrow key navigation
	)
	tsLog := table.DefaultStyles()
	tsLog.Header = tsLog.Header.BorderStyle(lipgloss.NormalBorder()).BorderForeground(lipgloss.Color("240")).BorderBottom(true).Bold(true).Foreground(lipgloss.Color("#EE6FF8"))
	tsLog.Selected = tsLog.Selected.Foreground(lipgloss.Color("229")).Background(lipgloss.Color("57")).Bold(false)
	tLog.SetStyles(tsLog)

	// K8s Table Setup with Focus enabled
	k8sCols := []table.Column{
		{Title: "POD NAME", Width: 35},
		{Title: "PHASE", Width: 15},
		{Title: "RESTARTS", Width: 10},
	}
	tK8s := table.New(
		table.WithColumns(k8sCols),
		table.WithHeight(7),
		table.WithFocused(true), // FIXED: Enables arrow key navigation
	)
	tsK8s := table.DefaultStyles()
	tsK8s.Header = tsK8s.Header.BorderStyle(lipgloss.NormalBorder()).BorderForeground(lipgloss.Color("240")).BorderBottom(true).Bold(true).Foreground(lipgloss.Color("#00ADD8"))
	tsK8s.Selected = tsK8s.Selected.Foreground(lipgloss.Color("229")).Background(lipgloss.Color("57")).Bold(false)
	tK8s.SetStyles(tsK8s)

	ti := textinput.New()
	ti.Placeholder = "Type to filter logs..."
	ti.Focus()
	ti.CharLimit = 50
	ti.Width = 40

	return model{
		activeTab:   0,
		tabs:        []string{"📊 Live Metrics", "🩺 System Health", "🚢 K8s Cluster"},
		logTable:    tLog,
		k8sTable:    tK8s,
		filterInput: ti,
		rpsHistory:  make([]float64, 0),
		health:      systemStatus{api: "WAITING", redis: "WAITING", redpanda: "WAITING"},
	}
}

func (m model) Init() tea.Cmd {
	return tea.Batch(textinput.Blink, tickEverySecond())
}

func tickEverySecond() tea.Cmd {
	return tea.Tick(time.Second, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

// --- DATA FETCHERS ---
func generateSparkline(data []float64) string {
	if len(data) == 0 {
		return ""
	}
	ticks := []rune{' ', '▂', '▃', '▄', '▅', '▆', '▇', '█'}
	min, max := data[0], data[0]
	for _, v := range data {
		if v < min {
			min = v
		}
		if v > max {
			max = v
		}
	}
	if min == max {
		line := ""
		for range data {
			line += string(ticks[0])
		}
		return line
	}
	var result string
	for _, v := range data {
		normalized := int((v - min) / (max - min) * 7.0)
		if normalized < 0 {
			normalized = 0
		}
		if normalized > 7 {
			normalized = 7
		}
		result += string(ticks[normalized])
	}
	return result
}

func fetchRealMetrics() metricsResponse {
	client := http.Client{Timeout: 1 * time.Second}
	resp, err := client.Get("http://localhost:8000/metrics")
	if err != nil || resp.StatusCode != http.StatusOK {
		return metricsResponse{}
	}
	defer resp.Body.Close()
	var metrics metricsResponse
	json.NewDecoder(resp.Body).Decode(&metrics)
	return metrics
}

func fetchSystemHealth() systemStatus {
	api, redisStat, redpanda := "OFFLINE", "OFFLINE", "OFFLINE"
	client := http.Client{Timeout: 1 * time.Second}
	if resp, err := client.Get("http://localhost:8000/"); err == nil {
		resp.Body.Close()
		if resp.StatusCode == http.StatusOK {
			api = "ONLINE"
		}
	}
	if conn, err := net.DialTimeout("tcp", "localhost:6379", 1*time.Second); err == nil {
		conn.Close()
		redisStat = "ONLINE"
	}
	if conn, err := net.DialTimeout("tcp", "localhost:19092", 1*time.Second); err == nil {
		conn.Close()
		redpanda = "ONLINE"
	}
	return systemStatus{api: api, redis: redisStat, redpanda: redpanda}
}

func fetchK8sPods() []table.Row {
	cmd := exec.Command("kubectl", "get", "pods", "-o", "json")
	out, err := cmd.Output()
	if err != nil {
		return []table.Row{{"kubectl error", err.Error(), ""}}
	}

	var podList struct {
		Items []struct {
			Metadata struct {
				Name string `json:"name"`
			} `json:"metadata"`
			Status struct {
				Phase             string `json:"phase"`
				ContainerStatuses []struct {
					RestartCount int `json:"restartCount"`
				} `json:"containerStatuses"`
			} `json:"status"`
		} `json:"items"`
	}

	if err := json.Unmarshal(out, &podList); err != nil {
		return []table.Row{{"Parse error", "", ""}}
	}

	var rows []table.Row
	for _, pod := range podList.Items {
		restarts := 0
		if len(pod.Status.ContainerStatuses) > 0 {
			restarts = pod.Status.ContainerStatuses[0].RestartCount
		}
		rows = append(rows, table.Row{
			pod.Metadata.Name,
			pod.Status.Phase,
			fmt.Sprintf("%d", restarts),
		})
	}
	return rows
}

// --- UPDATE LOGIC ---
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tickMsg:
		if m.activeTab == 0 {
			metrics := fetchRealMetrics()
			m.currentRPS = metrics.RPS
			m.avgLatency = metrics.AvgLatency
			if len(metrics.Logs) > 0 {
				m.recentLogs = metrics.Logs
			}

			m.rpsHistory = append(m.rpsHistory, float64(m.currentRPS))
			if len(m.rpsHistory) > 40 {
				m.rpsHistory = m.rpsHistory[1:]
			}

			var filteredRows []table.Row
			filterStr := strings.ToLower(m.filterInput.Value())
			for _, log := range m.recentLogs {
				displayID := log.ID
				if displayID == "" {
					displayID = "N/A"
				}
				if filterStr == "" || strings.Contains(strings.ToLower(log.Status), filterStr) || strings.Contains(strings.ToLower(displayID), filterStr) {
					filteredRows = append(filteredRows, table.Row{displayID, log.Amount, log.Status})
				}
			}
			m.logTable.SetRows(filteredRows)
		} else if m.activeTab == 1 {
			m.health = fetchSystemHealth()
		} else if m.activeTab == 2 {
			m.k8sTable.SetRows(fetchK8sPods())
		}
		cmds = append(cmds, tickEverySecond())

	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "esc":
			return m, tea.Quit
		case "tab":
			m.activeTab = (m.activeTab + 1) % len(m.tabs)
			return m, nil
		case "shift+tab":
			m.activeTab = (m.activeTab - 1 + len(m.tabs)) % len(m.tabs)
			return m, nil
		case "up", "down":
			// Explicitly forward arrow keys to the active table component
			if m.activeTab == 0 {
				m.logTable, cmd = m.logTable.Update(msg)
				return m, cmd
			} else if m.activeTab == 2 {
				m.k8sTable, cmd = m.k8sTable.Update(msg)
				return m, cmd
			}
		}
	}

	if m.activeTab == 0 {
		m.filterInput, cmd = m.filterInput.Update(msg)
		cmds = append(cmds, cmd)
	}

	return m, tea.Batch(cmds...)
}

// --- VIEW LOGIC ---
func (m model) View() string {
	header := titleStyle.Render("SENTINEL ML - COMMAND CENTER")

	var renderedTabs []string
	for i, t := range m.tabs {
		if i == m.activeTab {
			renderedTabs = append(renderedTabs, activeTabStyle.Render(t))
		} else {
			renderedTabs = append(renderedTabs, inactiveTabStyle.Render(t))
		}
	}
	tabRow := lipgloss.JoinHorizontal(lipgloss.Top, renderedTabs...)

	var content string

	if m.activeTab == 0 {
		rpsText := metricLabelStyle.Render("Live Throughput :") + metricValueStyle.Render(fmt.Sprintf("%d RPS", m.currentRPS))
		latText := metricLabelStyle.Render("Avg Latency     :") + metricValueStyle.Render(fmt.Sprintf("%.2f ms", m.avgLatency))
		sparkStr := generateSparkline(m.rpsHistory)
		sparkView := metricLabelStyle.Render("Traffic Trend   :") + "\n" + lipgloss.NewStyle().Foreground(lipgloss.Color("#00ADD8")).Render(sparkStr)
		metricsPanel := panelStyle.Render(lipgloss.JoinVertical(lipgloss.Left, rpsText, latText, "", sparkView))
		filterPanel := lipgloss.NewStyle().Padding(1, 0).Render(m.filterInput.View())
		tablePanel := baseStyle.Render(m.logTable.View())
		content = lipgloss.JoinVertical(lipgloss.Left, metricsPanel, filterPanel, tablePanel)
	} else if m.activeTab == 1 {
		apiStr := offlineStyle.Render(m.health.api)
		if m.health.api == "ONLINE" {
			apiStr = onlineStyle.Render(m.health.api)
		}
		redisStr := offlineStyle.Render(m.health.redis)
		if m.health.redis == "ONLINE" {
			redisStr = onlineStyle.Render(m.health.redis)
		}
		kafkaStr := offlineStyle.Render(m.health.redpanda)
		if m.health.redpanda == "ONLINE" {
			kafkaStr = onlineStyle.Render(m.health.redpanda)
		}
		healthView := "API Gateway (Go) : " + apiStr + "\n" +
			"Redis Cache      : " + redisStr + "\n" +
			"Redpanda Broker  : " + kafkaStr + "\n"
		content = panelStyle.Render(healthView)
	} else if m.activeTab == 2 {
		k8sPanel := baseStyle.Render(m.k8sTable.View())
		infoText := helpStyle.Render("Live querying `kubectl get pods` from local context.")
		content = lipgloss.JoinVertical(lipgloss.Left, k8sPanel, infoText)
	}

	footer := helpStyle.Render("Tab: Switch Menus • Arrows: Navigate Tables • Esc: Quit")
	ui := lipgloss.JoinVertical(lipgloss.Left, header, tabRow, "", content, "", footer)
	return lipgloss.NewStyle().Padding(1, 4).Render(ui)
}

func main() {
	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running TUI: %v\n", err)
		os.Exit(1)
	}
}
