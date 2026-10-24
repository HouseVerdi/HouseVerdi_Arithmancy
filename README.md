# HouseVerdi Arithmancy

Author: Claudio Verdi  
GitHub: https://github.com/HouseVerdi/HouseVerdi_Arithmancy

## Overview

HouseVerdi Arithmancy is an educational web application combining
numerology calculations with AI-generated reflections.

It supports personal profiles and couple compatibility, with guidance
for relationships, friendships and colleagues.

Numerology results and compatibility percentages are symbolic,
for entertainment and reflection. They are not scientific predictions.

## Development history

The project started in Google Antigravity, where its initial structure
and core functionality took shape. When the available usage quota was
reached, development continued with assistance from ChatGPT.

Claudio Verdi directed the requirements, tested the application and
deployed it on AWS.

## Features

- Personal Calculation and Couple Compatibility.
- Pythagorean, Chaldean, Chinese Kua and Indian/Vedic calculations.
- Colour numerology and zodiac information.
- AI-generated guidance for partner, friend and colleague roles.
- Responsive interface.
- Server-side validation of names, dates and request structure.

## Technology

- Frontend: HTML, CSS and JavaScript.
- Backend: Python and Flask.
- Generative AI: Amazon Bedrock through boto3.
- Model ID: eu.amazon.nova-micro-v1:0.
- Bedrock region: eu-north-1.
- Hosting: AWS EC2 with Ubuntu 24.04 LTS.
- Web server: Nginx.
- Application server: Gunicorn, managed by systemd.

## Project files

- app.py: Flask routes, validation and AI reading requests.
- ai_service.py: Amazon Bedrock integration.
- numerology_system.py: Python calculations.
- templates/index.html: interface and browser-side calculations.
- requirements.txt: Python dependencies.
- .gitignore: excludes environments, caches and secret files.

## Local setup on Linux

Requires Python 3 with venv support, Git and AWS credentials with
permission to invoke the selected Bedrock model.

```bash
git clone https://github.com/HouseVerdi/HouseVerdi_Arithmancy.git
cd HouseVerdi_Arithmancy
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export BEDROCK_REGION=eu-north-1
export BEDROCK_MODEL_ID=eu.amazon.nova-micro-v1:0
python app.py
```

Open http://127.0.0.1:5000 in a browser.

Configure AWS authentication separately using a supported boto3
credential provider. Never commit access keys or credentials.
On EC2, an IAM role can provide temporary credentials.

## Deployed architecture

The browser sends HTTP requests to Nginx on port 80.
Nginx forwards them to Gunicorn on 127.0.0.1:8000.
Gunicorn runs Flask, which calls Amazon Bedrock for generated text.

The deployed systemd service is named houseverdi.

The interface calculates its displayed results in JavaScript.
The backend also performs Python calculations and uses calculated
symbols to request AI guidance. The browser displays the returned
interpretations.

## Verification on 24 October 2026

- SSH connection to the EC2 instance succeeded.
- houseverdi and nginx services were active and enabled.
- Local HTTP request returned 200 OK.
- Nginx configuration test passed.
- Direct Bedrock test returned generated text.
- Personal and couple modes displayed AI-generated guidance.
- An API request without names returned 400 Bad Request:
  "Enter first and last names."

These checks do not constitute a complete automated test suite.

## Limitations and improvements

AI text may contain errors. During a personal-profile test, generated
guidance incorrectly referred to Soul Urge 9 although the displayed
calculation was 8. Generated numerical statements need stronger
validation.

Browser and backend calculations are maintained separately.
Consolidating them would reduce the risk of inconsistent results.

Kua uses a Gregorian birth-year approximation. For Non-Binary profiles,
the current implementation uses the female Kua formula.

The current deployment uses HTTP. HTTPS, authentication and rate
limiting are further improvements.
