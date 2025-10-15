import great_expectations as gx
import pandas as pd
import json
from datetime import datetime
import os

# Load the data
df = pd.read_csv("DS/data/Flipkart/FiPhones_17-08-25.csv")

# Initialize Great Expectations context
context = gx.get_context()
data_source = context.data_sources.add_pandas("pandas")
data_asset = data_source.add_dataframe_asset(name="iphone_dataframe_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("iphone_batch_definition")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

# List to store all validation results
validation_results = []
expectation_details = []

# 1. Original expectation - Max Order Quantity validation
expectation_1 = gx.expectations.ExpectColumnValuesToBeBetween(
    column="maxOrderQuantityAllowed", 
    min_value=1, 
    max_value=1000
)
result_1 = batch.validate(expectation_1)
validation_results.append(result_1)
expectation_details.append({
    "id": 1,
    "name": "Max Order Quantity Range",
    "expectation_type": "ExpectColumnValuesToBeBetween",
    "column": "maxOrderQuantityAllowed",
    "parameters": {"min_value": 1, "max_value": 1000}
})

# 2. Availability State validation - should only contain valid stock statuses
expectation_2 = gx.expectations.ExpectColumnValuesToBeInSet(
    column="availability_displayState",
    value_set=["IN_STOCK", "OUT_OF_STOCK", "LIMITED_STOCK", "TEMPORARILY_UNAVAILABLE"]
)
result_2 = batch.validate(expectation_2)
validation_results.append(result_2)
expectation_details.append({
    "id": 2,
    "name": "Valid Stock Status",
    "expectation_type": "ExpectColumnValuesToBeInSet",
    "column": "availability_displayState",
    "parameters": {"value_set": ["IN_STOCK", "OUT_OF_STOCK", "LIMITED_STOCK", "TEMPORARILY_UNAVAILABLE"]}
})

# 3. Pricing validation - Final price should be less than or equal to MRP
# Fixed the expectation name
expectation_3 = gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
    column_A="pricing_mrp_value",
    column_B="pricing_finalPrice_value",
    or_equal=True
)
result_3 = batch.validate(expectation_3)
validation_results.append(result_3)
expectation_details.append({
    "id": 3,
    "name": "MRP >= Final Price",
    "expectation_type": "ExpectColumnPairValuesAToBeGreaterThanB",
    "column": "pricing_mrp_value vs pricing_finalPrice_value",
    "parameters": {"column_A": "pricing_mrp_value", "column_B": "pricing_finalPrice_value", "or_equal": True}
})

# 4. Rating validation - Average rating should be between 1 and 5
expectation_4 = gx.expectations.ExpectColumnValuesToBeBetween(
    column="rating_average",
    min_value=1.0,
    max_value=5.0
)
result_4 = batch.validate(expectation_4)
validation_results.append(result_4)
expectation_details.append({
    "id": 4,
    "name": "Rating Range 1-5",
    "expectation_type": "ExpectColumnValuesToBeBetween",
    "column": "rating_average",
    "parameters": {"min_value": 1.0, "max_value": 5.0}
})

# 5. Rating count validation - Should be non-negative
expectation_5 = gx.expectations.ExpectColumnValuesToBeBetween(
    column="rating_count",
    min_value=0
)
result_5 = batch.validate(expectation_5)
validation_results.append(result_5)
expectation_details.append({
    "id": 5,
    "name": "Non-negative Rating Count",
    "expectation_type": "ExpectColumnValuesToBeBetween",
    "column": "rating_count",
    "parameters": {"min_value": 0}
})

# 6. Review count validation - Should be non-negative
expectation_6 = gx.expectations.ExpectColumnValuesToBeBetween(
    column="rating_reviewCount",
    min_value=0
)
result_6 = batch.validate(expectation_6)
validation_results.append(result_6)
expectation_details.append({
    "id": 6,
    "name": "Non-negative Review Count",
    "expectation_type": "ExpectColumnValuesToBeBetween",
    "column": "rating_reviewCount",
    "parameters": {"min_value": 0}
})

# 7. Title validation - Should not be null
expectation_7 = gx.expectations.ExpectColumnValuesToNotBeNull(
    column="titles_title"
)
result_7 = batch.validate(expectation_7)
validation_results.append(result_7)
expectation_details.append({
    "id": 7,
    "name": "Title Not Null",
    "expectation_type": "ExpectColumnValuesToNotBeNull",
    "column": "titles_title",
    "parameters": {}
})

# 8. Title should contain "iPhone"
expectation_8 = gx.expectations.ExpectColumnValuesToMatchRegex(
    column="titles_title",
    regex=r".*iPhone.*"
)
result_8 = batch.validate(expectation_8)
validation_results.append(result_8)
expectation_details.append({
    "id": 8,
    "name": "Title Contains iPhone",
    "expectation_type": "ExpectColumnValuesToMatchRegex",
    "column": "titles_title",
    "parameters": {"regex": ".*iPhone.*"}
})

# 9. Key specs validation - Should not be null
expectation_9 = gx.expectations.ExpectColumnValuesToNotBeNull(
    column="keySpecs"
)
result_9 = batch.validate(expectation_9)
validation_results.append(result_9)
expectation_details.append({
    "id": 9,
    "name": "Key Specs Not Null",
    "expectation_type": "ExpectColumnValuesToNotBeNull",
    "column": "keySpecs",
    "parameters": {}
})

# 10. Media images validation - Should contain valid image URLs
expectation_10 = gx.expectations.ExpectColumnValuesToMatchRegex(
    column="media_images",
    regex=r"https://.*\.jpeg.*"
)
result_10 = batch.validate(expectation_10)
validation_results.append(result_10)
expectation_details.append({
    "id": 10,
    "name": "Valid Image URLs",
    "expectation_type": "ExpectColumnValuesToMatchRegex",
    "column": "media_images",
    "parameters": {"regex": "https://.*\\.jpeg.*"}
})

# 11-15. Additional expectations (shortened for brevity)
additional_expectations = [
    (gx.expectations.ExpectColumnValuesToBeBetween(column="pricing_discountAmount", min_value=0), "Discount Amount >= 0"),
    (gx.expectations.ExpectColumnValuesToBeBetween(column="pricing_totalDiscount", min_value=0), "Total Discount >= 0"),
    (gx.expectations.ExpectColumnValuesToMatchRegex(column="keySpecs", regex=r".*(GB|TB).*"), "Storage Specs Present"),
    (gx.expectations.ExpectColumnValuesToMatchRegex(column="keySpecs", regex=r".*(cm|inch).*"), "Display Size Present"),
    (gx.expectations.ExpectColumnValuesToMatchRegex(column="keySpecs", regex=r".*MP.*"), "Camera Specs Present")
]

for i, (expectation, name) in enumerate(additional_expectations, 11):
    result = batch.validate(expectation)
    validation_results.append(result)
    expectation_details.append({
        "id": i,
        "name": name,
        "expectation_type": expectation.expectation_type,
        "column": expectation.configuration.kwargs.get('column', 'N/A'),
        "parameters": {k: v for k, v in expectation.configuration.kwargs.items() if k != 'column'}
    })

# Essential columns validation
essential_columns = ["availability_displayState", "pricing_finalPrice_value", "pricing_mrp_value", "titles_title"]

for i, col in enumerate(essential_columns, 16):
    expectation = gx.expectations.ExpectColumnValuesToNotBeNull(column=col)
    result = batch.validate(expectation)
    validation_results.append(result)
    expectation_details.append({
        "id": i,
        "name": f"{col} Not Null",
        "expectation_type": "ExpectColumnValuesToNotBeNull",
        "column": col,
        "parameters": {}
    })

# Print validation results
print("=== GREAT EXPECTATIONS VALIDATION RESULTS ===\n")
for i, result in enumerate(validation_results, 1):
    expectation_type = result.expectation_config.expectation_context
    column = result.expectation_config.kwargs.get('column', 'N/A')
    success = result.success
    
    print(f"{i}. {expectation_type}")
    print(f"   Column: {column}")
    print(f"   Success: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if not success:
        print(f"   Details: {result.result}")
    print()

# Summary
total_expectations = len(validation_results)
passed_expectations = sum(1 for result in validation_results if result.success)
failed_expectations = total_expectations - passed_expectations

print("=== VALIDATION SUMMARY ===")
print(f"Total Expectations: {total_expectations}")
print(f"Passed: {passed_expectations}")
print(f"Failed: {failed_expectations}")
print(f"Success Rate: {(passed_expectations/total_expectations)*100:.1f}%")

# Create comprehensive results summary
results_summary = {
    "validation_run_info": {
        "timestamp": datetime.now().isoformat(),
        "dataset": "Flipkart iPhones Dataset",
        "total_rows": len(df),
        "total_columns": len(df.columns)
    },
    "overall_summary": {
        "total_expectations": total_expectations,
        "passed_expectations": passed_expectations,
        "failed_expectations": failed_expectations,
        "success_rate_percentage": round((passed_expectations/total_expectations)*100, 2)
    },
    "detailed_results": []
}

# Add detailed results
for i, (result, detail) in enumerate(zip(validation_results, expectation_details)):
    result_detail = {
        "expectation_id": detail["id"],
        "expectation_name": detail["name"],
        "expectation_type": detail["expectation_type"],
        "column": detail["column"],
        "parameters": detail["parameters"],
        "success": result.success,
        "result_details": {
            "observed_value": getattr(result.result, 'observed_value', None),
            "element_count": getattr(result.result, 'element_count', None),
            "missing_count": getattr(result.result, 'missing_count', None),
            "missing_percent": getattr(result.result, 'missing_percent', None),
            "unexpected_count": getattr(result.result, 'unexpected_count', None),
            "unexpected_percent": getattr(result.result, 'unexpected_percent', None)
        }
    }
    results_summary["detailed_results"].append(result_detail)

# Create expectation suite
try:
    expectation_suite_name = "iphone_data_quality_suite"
    suite = gx.ExpectationSuite(name=expectation_suite_name)
    
    # Add all expectations to the suite
    all_expectations = [
        expectation_1, expectation_2, expectation_3, expectation_4, expectation_5,
        expectation_6, expectation_7, expectation_8, expectation_9, expectation_10
    ]
    
    # Add additional expectations
    for expectation, _ in additional_expectations:
        all_expectations.append(expectation)
    
    # Add essential column expectations
    for col in essential_columns:
        all_expectations.append(gx.expectations.ExpectColumnValuesToNotBeNull(column=col))
    
    for expectation in all_expectations:
        suite.add_expectation(expectation)
    
    # Save suite to context
    context.suites.add(suite)
    
    print(f"\n✅ Created expectation suite: '{expectation_suite_name}'")
    
    # Export suite to JSON file
    suite_dict = suite.to_json_dict()
    os.makedirs("exports", exist_ok=True)
    
    with open("exports/iphone_expectation_suite.json", "w") as f:
        json.dump(suite_dict, f, indent=2)
    
    print(f"📄 Exported suite to: exports/iphone_expectation_suite.json")
    
except Exception as e:
    print(f"Note: Could not create expectation suite - {e}")

# Export results summary
try:
    with open("exports/validation_results_summary.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"📊 Exported results summary to: exports/validation_results_summary.json")
    
except Exception as e:
    print(f"Error exporting results: {e}")

print("\nValidation completed! 🎉")
print("Check the 'exports' folder for both suite and results files.")