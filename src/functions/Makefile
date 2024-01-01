invoke: invoke-create-schema

invoke-create-schema:
	sam local invoke \
		CreateSchemaLambda \
		--event ./create-schema/event.json \
		-t ../../resources/cdk.out/DocumentAIStack.template.json
