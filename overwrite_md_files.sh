#!/bin/bash
# /Users/Hiro/Downloads/files2/ から docs/ へ上書きコピー

SRC=/Users/Hiro/Downloads/files2
DST=/Users/Hiro/git_lesson/ai_chat

cp -p $SRC/glossary.md              $DST/docs/overview/glossary.md
cp -p $SRC/project_background.md    $DST/docs/overview/project_background.md
cp -p $SRC/system_overview.md       $DST/docs/overview/system_overview.md

cp -p $SRC/business_requirements.md     $DST/docs/requirements/business_requirements.md
cp -p $SRC/functional_requirements.md   $DST/docs/requirements/functional_requirements.md
cp -p $SRC/nonfunctional_requirements.md $DST/docs/requirements/nonfunctional_requirements.md
cp -p $SRC/use_cases.md             $DST/docs/requirements/use_cases.md

cp -p $SRC/architecture_design.md   $DST/docs/design/architecture_design.md
cp -p $SRC/screen_transition.md     $DST/docs/design/screen_transition.md
cp -p $SRC/sequence_diagrams.md     $DST/docs/design/sequence_diagrams.md
cp -p $SRC/ui_design.md             $DST/docs/design/ui_design.md

cp -p $SRC/table_definition.md      $DST/docs/data/table_definition.md
cp -p $SRC/er_diagram.md            $DST/docs/data/er_diagram.md
cp -p $SRC/data_flow.md             $DST/docs/data/data_flow.md

cp -p $SRC/api_specification.md     $DST/docs/specifications/api_specification.md
cp -p $SRC/batch_specification.md   $DST/docs/specifications/batch_specification.md
cp -p $SRC/error_handling.md        $DST/docs/specifications/error_handling.md
cp -p $SRC/program_specification.md $DST/docs/specifications/program_specification.md

cp -p $SRC/runbook.md               $DST/docs/operations/runbook.md
cp -p $SRC/release_procedure.md     $DST/docs/operations/release_procedure.md
cp -p $SRC/incident_response.md     $DST/docs/operations/incident_response.md

cp -p $SRC/test_plan.md             $DST/docs/testing/test_plan.md
cp -p $SRC/test_cases.md            $DST/docs/testing/test_cases.md
cp -p $SRC/test_results.md          $DST/docs/testing/test_results.md

echo "✅ コピー完了"
