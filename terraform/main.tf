# main.tf

# Variables
variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub username or organization"
  type        = string
  default     = "DaveStutler"
}

variable "repository_name" {
  description = "Name of the GitHub repository"
  type        = string
  default     = "aws-rekognition-image-analyzer"
}

variable "repository_description" {
  description = "Description for the GitHub repository"
  type        = string
  default     = "AWS Rekognition Image Analysis Tool with Visual Bounding Boxes and Web Reports"
}

# Local variables for file contents
locals {
  readme_content = <<-EOT
# AWS Rekognition Image Analyzer 🔍

A comprehensive Python tool for analyzing images using AWS Rekognition with visual bounding boxes and detailed reports.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Rekognition-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features ✨

- **Face Detection**: Detect faces with age, gender, and emotion analysis
- **Object Detection**: Identify objects and labels with confidence scores
- **Visual Bounding Boxes**: See exactly what was detected with colored boxes
- **Multiple Output Formats**: 
  - Interactive matplotlib plots
  - Web-based HTML reports
  - Saved PNG images
- **Dual Mode**: Analyze sample images or upload your own
- **Professional Reports**: Beautiful HTML reports with statistics

## Prerequisites 📋

- Python 3.8 or higher
- AWS Account with Rekognition access
- AWS CLI configured with credentials

## Installation 🚀

1. **Clone the repository:**
   ```bash
   git clone https://github.com/${var.github_owner}/${var.repository_name}.git
   cd ${var.repository_name}
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

## Usage 💡

### Basic Usage
```bash
python lambda/image_test.py
```

### Options
1. **Sample Images**: Analyze curated test images from the internet
2. **Custom Images**: Upload and analyze your own image files

## AWS Permissions 🔐

Your AWS user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectFaces",
                "rekognition:DetectLabels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Output Examples 📊

### Face Detection
- Age range estimation
- Gender detection  
- Emotion analysis
- Confidence scores
- Visual bounding boxes

### Object Detection
- Object identification
- Confidence percentages
- Instance counting
- Location mapping

## Project Structure 📁

```
${var.repository_name}/
├── lambda/
│   └── image_test.py          # Main analysis script
├── requirements.txt           # Python dependencies
├── main.tf                   # Terraform configuration
├── versions.tf               # Terraform version constraints
├── providers.tf              # Provider configurations
├── .gitignore               # Git ignore patterns
└── README.md                # This file
```

## Output Directories 📂

- `rekognition_output/`: Matplotlib PNG files
- `rekognition_web_output/`: HTML reports and annotated images

## Features in Detail 🔍

### Visual Analysis
- **Colored bounding boxes** around detected faces and objects
- **Confidence scores** displayed on each detection
- **Age and emotion labels** for faces
- **Object classification** with percentage confidence

### Web Reports
- **Professional HTML layout** with CSS styling
- **Interactive image viewing** with annotations
- **Detailed statistics** and summaries
- **Responsive design** for different screen sizes

## Troubleshooting 🔧

### Matplotlib Display Issues
The script automatically handles display issues by:
1. Trying multiple backends (Qt5Agg, TkAgg, etc.)
2. Falling back to file saving
3. Generating web-based reports as backup

### Common Issues
- **No camera needed**: This tool works with static images only
- **AWS credentials**: Ensure `aws configure` is properly set up
- **Permissions**: Verify Rekognition permissions in your AWS account

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- AWS Rekognition for powerful computer vision capabilities
- Matplotlib and PIL for visualization tools
- The open-source community for inspiration and tools
- Claude 4 for assistance in development

---

**Created with Terraform** 🏗️ | **Powered by AWS Rekognition** ⚡ | **Built with Python** 🐍
EOT

  gitignore_content = <<-EOT
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv/
.env/

# AWS
.aws/
credentials
config

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
rekognition_output/
rekognition_web_output/
*.png
*.jpg
*.jpeg
*.gif
*.html

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfplan
terraform.tfvars

# Logs
*.log
EOT


}

# Create GitHub repository
resource "github_repository" "rekognition_analyzer" {
  name         = var.repository_name
  description  = var.repository_description
  visibility   = "public"  # Change to "private" if you want a private repo
  
  has_issues    = true
  has_projects  = true
  has_wiki      = true
  has_downloads = true
  
  auto_init          = true
  gitignore_template = "Python"
  license_template   = "mit"
  
  topics = ["aws", "rekognition", "python", "computer-vision", "image-analysis", "terraform"]
  
  # Enable vulnerability alerts
  vulnerability_alerts = true
  
  # Branch protection (optional)
  # delete_branch_on_merge = true
}

# Create repository files
resource "github_repository_file" "readme" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "README.md"
  content            = local.readme_content
  commit_message     = "Add README.md via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "requirements" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "requirements.txt"
  content            = file("${path.module}/requirements.txt")
  commit_message     = "Add requirements.txt via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "gitignore" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = ".gitignore"
  content            = local.gitignore_content
  commit_message     = "Add .gitignore via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "main_tf" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "terraform/main.tf"
  content            = file("${path.module}/main.tf")
  commit_message     = "Add Terraform configuration via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "versions_tf" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "terraform/versions.tf"
  content            = file("${path.module}/versions.tf")
  commit_message     = "Add Terraform versions via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "providers_tf" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"  
  file               = "terraform/providers.tf"
  content            = file("${path.module}/providers.tf")
  commit_message     = "Add Terraform providers via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "image_test_py" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "lambda/images.py"
  content            = file("${path.module}/lambda/images.py")
  commit_message     = "Add image analysis script via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "camera_test_py" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "lambda/camera_test.py"
  content            = file("${path.module}/lambda/camera_test.py")
  commit_message     = "Add camera script via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

resource "github_repository_file" "video_stream_py" {
  repository          = github_repository.rekognition_analyzer.name
  branch             = "master"
  file               = "lambda/video_stream.py"
  content            = file("${path.module}/lambda/video_stream.py")
  commit_message     = "Add video stream script via Terraform"
  commit_author      = var.github_owner
  commit_email       = "${var.github_owner}@users.noreply.github.com"
  overwrite_on_create = true
}

# Create branch protection rule (optional)
resource "github_branch_protection" "main_branch_protection" {
  repository_id = github_repository.rekognition_analyzer.name
  pattern       = "main"
  
  enforce_admins         = false
  allows_deletions      = false
  allows_force_pushes   = false
  required_linear_history = true
  
  required_status_checks {
    strict = false
  }
}

# Create repository topics
resource "github_repository_topics" "rekognition_topics" {
  repository = github_repository.rekognition_analyzer.name
  topics = [
    "aws",
    "rekognition", 
    "python",
    "computer-vision",
    "image-analysis",
    "terraform",
    "machine-learning",
    "face-detection",
    "object-detection"
  ]
}

# Outputs
output "repository_url" {
  description = "URL of the created GitHub repository"
  value       = github_repository.rekognition_analyzer.html_url
}

output "repository_clone_url" {
  description = "HTTPS clone URL for the repository"
  value       = github_repository.rekognition_analyzer.http_clone_url
}

output "repository_ssh_clone_url" {
  description = "SSH clone URL for the repository"
  value       = github_repository.rekognition_analyzer.ssh_clone_url
}