CONFIG = config.mk
include ${CONFIG}

ifdef CI
ENV := $(CI_ENVIRONMENT_NAME)
endif

ifndef ENV
ENV := Prod
else
ENV := $(shell echo ${ENV} | awk '{print toupper(substr($$0,1,1)) tolower(substr($$0,2))}')
endif

ifndef REGION
REGION := eu-west-3
endif

ifdef TARGET
TARGET := "-target=${TARGET}"
endif

PROFILE := aribas-training
ifdef CI
AWS_PROFILE_ENV :=
TF_BACKEND_CONFIG_PROFILE :=
else
AWS_PROFILE_ENV := AWS_PROFILE=$(PROFILE)
TF_BACKEND_CONFIG_PROFILE := -backend-config="profile=$(PROFILE)"
endif
ACCOUNT_ID := $(shell $(AWS_PROFILE_ENV) aws sts get-caller-identity --query Account --output text)

ifdef GITHUB_SHA
GIT_SHA := $(GITHUB_SHA)
else
GIT_SHA := $(shell git log -n1 --format=format:"%H")
endif

BUCKET_NAME := terraform-states-$(ACCOUNT_ID)
STATE_REGION := eu-west-3

PLAN_BUCKET_NAME := terraform-plans-$(ACCOUNT_ID)

REPOSITORY := $(shell git remote get-url origin | sed 's/^.*@//g;s/^.*https\?:\/\///g;s/\.git.*$$//g;s/:/\//')

TF_VARS := -var 'account_id=$(ACCOUNT_ID)' \
  -var 'plan_name=$(PLAN_NAME)' \
  -var 'repository=$(REPOSITORY)' \
  -var 'env=$(ENV)' \
  -var 'region=$(REGION)'

all:
	@echo "Usage: [ENV=dev|prod] make <init|plan|apply>"

plan: tf-get tf-plan
apply: tf-get tf-apply
ifdef CI
plan-save-output: tf-get tf-plan-save-output-no-color
else
plan-save-output: tf-get tf-plan-save-output
endif
apply-from-plan: tf-get tf-apply-from-plan
refresh: tf-refresh
ifdef CI
destroy: tf-destroy-auto-approve
else
destroy: tf-destroy
endif
output: tf-output
import: tf-import
providers-lock: tf-providers-lock
ifdef CI
validate: tf-init-empty-backend tf-validate-no-color
else
validate: tf-validate
endif

$(info Using Account: $(PROFILE))
$(info Using Region: $(REGION))

tf-get:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform get -update

tf-plan:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform plan $(TF_VARS) $(TARGET)

tf-apply:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform apply $(TF_VARS) $(TARGET)

tf-plan-save-output:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) $(TF_IN_AUTOMATION) \
	terraform plan $(TF_VARS) $(TARGET) -out=./terraform.plan && \
	$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	aws s3 cp ./terraform.plan s3://$(PLAN_BUCKET_NAME)/$(PLAN_NAME)/$(REGION)/$(GIT_SHA).terraform.plan && \
	rm ./terraform.plan

tf-plan-save-output-no-color:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) $(TF_IN_AUTOMATION) \
	terraform plan $(TF_VARS) $(TARGET) -out=./terraform.plan -no-color && \
	$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	aws s3 cp ./terraform.plan s3://$(PLAN_BUCKET_NAME)/$(PLAN_NAME)/$(REGION)/$(GIT_SHA).terraform.plan && \
	rm ./terraform.plan

tf-apply-from-plan:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	aws s3 cp s3://$(PLAN_BUCKET_NAME)/$(PLAN_NAME)/$(REGION)/$(GIT_SHA).terraform.plan ./terraform.plan && \
	$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) $(TF_IN_AUTOMATION) \
	terraform apply ./terraform.plan && \
	rm ./terraform.plan

tf-refresh:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform refresh $(TF_VARS) $(TARGET)

tf-destroy:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform destroy $(TF_VARS) $(TARGET)

tf-destroy-auto-approve:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform destroy $(TF_VARS) $(TARGET) -auto-approve

tf-output:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform output

tf-import:
	@$(AWS_PROFILE_ENV) AWS_DEFAULT_REGION=$(REGION) \
	terraform import $(TF_VARS) $(IMPORT_ADDR) $(IMPORT_ID)

tf-providers-lock:
	@rm -f .terraform.lock.hcl && \
	terraform providers lock -platform=darwin_amd64 -platform=linux_amd64

tf-init-empty-backend:
	terraform init -backend=false

# Region should be explicitly set for providers when running "validate", see
# https://github.com/hashicorp/terraform/pull/24896#issuecomment-722483177
tf-validate:
	AWS_DEFAULT_REGION=$(STATE_REGION) terraform validate && \
	terraform fmt -check -write=false

tf-validate-no-color:
	AWS_DEFAULT_REGION=$(STATE_REGION) terraform validate -no-color && \
	terraform fmt -check -write=false
init:
	@$(AWS_PROFILE_ENV) terraform init $(TF_BACKEND_CONFIG_PROFILE) \
		-backend-config="region=$(STATE_REGION)" \
		-backend-config="bucket=$(BUCKET_NAME)" \
		-backend-config="key=${PLAN_NAME}/${REGION}.tfstate" \
		-reconfigure

.PHONY: all init plan apply validate git-pull tf-plan tf-apply tf-init-empty-backend
