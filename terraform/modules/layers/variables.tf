variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "serverless_utils_zip_path" {
  description = "Path to the serverless utils zip file"
  type        = string
}

variable "serverless_utils_runtime" {
  description = "Runtime for the serverless utils Lambda layer"
  type        = list(string)
  default     = ["python3.14"]
}

variable "serverless_utils_compatible_architectures" {
  description = "Compatible architectures for the serverless utils Lambda layer"
  type        = list(string)
  default     = ["x86_64", "arm64"]
}

variable "image_processing_zip_path" {
  description = "Path to the Image Processing zip file"
  type        = string
}

variable "image_processing_runtime" {
  description = "Runtime for the Image Processing Lambda layer"
  type        = list(string)
  default     = ["python3.14"]
}

variable "image_processing_compatible_architectures" {
  description = "Compatible architectures for the Image Processing Lambda layer"
  type        = list(string)
  default     = ["arm64"]
}
