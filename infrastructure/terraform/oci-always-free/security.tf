resource "oci_core_default_security_list" "sentinel_security_list" {
  manage_default_resource_id = oci_core_vcn.sentinel_vcn.default_security_list_id
  display_name               = "sentinel-security-list"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6" # TCP protokol numarası
    source   = "0.0.0.0/0"
    tcp_options {
      max = 22
      min = 22
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 8000
      min = 8000
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      max = 8080
      min = 8080
    }
  }
}
