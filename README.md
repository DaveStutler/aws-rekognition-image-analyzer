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
   git clone https://github.com/DaveStutler/aws-rekognition-image-analyzer.git
   cd aws-rekognition-image-analyzer
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
aws-rekognition-image-analyzer/
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
