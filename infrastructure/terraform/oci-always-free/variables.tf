variable "tenancy_ocid" {
  description = "The OCID of your OCI tenancy."
  type        = string
}

variable "user_ocid" {
  description = "The OCID of the user calling the API."
  type        = string
}

variable "fingerprint" {
  description = "The fingerprint of the public key."
  type        = string
}

variable "private_key_path" {
  description = "The absolute path to the downloaded .pem private key file."
  type        = string
}

variable "region" {
  description = "The OCI region (e.g., eu-frankfurt-1)."
  type        = string
}

variable "compartment_ocid" {
  description = "The OCID of the compartment where resources will be created. (For Free Tier, this is usually the same as your tenancy_ocid)."
  type        = string
}

variable "ssh_public_key_path" {
  description = "The absolute path to your public SSH key for the compute instance."
  type        = string
}
