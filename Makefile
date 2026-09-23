.PHONY: help install test lint format clean terraform-init terraform-plan terraform-apply terraform-destroy

help:
	@echo "SageMaker Model Monitor Starter - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install Python dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test            Run tests"
	@echo "  make lint            Run linters (flake8)"
	@echo "  make format          Format code (black, isort)"
	@echo ""
	@echo "Terraform:"
	@echo "  make terraform-init  Initialize Terraform"
	@echo "  make terraform-plan  Plan Terraform changes"
	@echo "  make terraform-apply Apply Terraform changes"
	@echo "  make terraform-destroy Destroy Terraform resources"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           Remove generated files and caches"

install:
	pip install -r requirements.txt
	pip install pytest flake8 black isort

test:
	pytest tests/ -v

lint:
	flake8 src/ scripts/ tests/ --max-line-length=120 --extend-ignore=E203,W503
	black --check src/ scripts/ tests/
	isort --check-only src/ scripts/ tests/

format:
	black src/ scripts/ tests/
	isort src/ scripts/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dist/ build/

terraform-init:
	cd infra && terraform init

terraform-plan:
	cd infra && terraform plan

terraform-apply:
	cd infra && terraform apply

terraform-destroy:
	cd infra && terraform destroy
