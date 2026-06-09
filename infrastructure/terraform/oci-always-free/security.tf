resource "oci_core_default_security_list" "sentinel_security_list" {
  manage_default_resource_id = oci_core_vcn.sentinel_vcn.default_security_list_id
  display_name               = "sentinel-security-list"

  # Egress: Makinenin dışarıya (internete) çıkışına tam izin veriyoruz. (Örn: apt-get update yapabilmek için)
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  # Ingress 1: SSH (Port 22) - Sunucuya terminalden sızıp yönetebilmemiz için.
  ingress_security_rules {
    protocol = "6" # TCP protokol numarası
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  # Ingress 2: Sentinel API & Dashboard (Port 8000) - HTMX arayüzünü tarayıcıdan açabilmek için.
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 8000
      min = 8000
    }
  }

  # Ingress 3: Redpanda Console (Port 8080) - Kafka akışını canlı izleyebilmek için.
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 8080
      min = 8080
    }
  }
}
