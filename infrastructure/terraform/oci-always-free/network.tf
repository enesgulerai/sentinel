resource "oci_core_vcn" "sentinel_vcn" {
  compartment_id = var.compartment_ocid
  cidr_block     = "10.0.0.0/16"
  display_name   = "sentinel-production-vcn"
  dns_label      = "sentinelvcn"
}

resource "oci_core_internet_gateway" "sentinel_igw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.sentinel_vcn.id
  display_name   = "sentinel-igw"
  enabled        = true
}

resource "oci_core_default_route_table" "sentinel_public_rt" {
  manage_default_resource_id = oci_core_vcn.sentinel_vcn.default_route_table_id
  display_name               = "sentinel-public-route"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.sentinel_igw.id
  }
}

resource "oci_core_subnet" "sentinel_public_subnet" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.sentinel_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "sentinel-public-subnet"
  dns_label         = "sentinelpub"
  route_table_id    = oci_core_vcn.sentinel_vcn.default_route_table_id
}
