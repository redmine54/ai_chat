#!/bin/bash

echo "Creating /docs directory structure..."

# Create directories
mkdir -p docs/{overview,requirements,specifications,design,data,operations,testing}

# Create files
touch docs/README.md

touch docs/overview/{README.md,project_background.md,system_overview.md,glossary.md}

touch docs/requirements/{README.md,business_requirements.md,functional_requirements.md,nonfunctional_requirements.md,use_cases.md}

touch docs/specifications/{README.md,program_specification.md,api_specification.md,batch_specification.md,error_handling.md}

touch docs/design/{README.md,ui_design.md,screen_transition.md,architecture_design.md,sequence_diagrams.md}

touch docs/data/{README.md,er_diagram.md,table_definition.md,data_flow.md}

touch docs/operations/{README.md,runbook.md,release_procedure.md,incident_response.md}

touch docs/testing/{README.md,test_plan.md,test_cases.md,test_results.md}

echo "All documentation directories and files have been created successfully."

