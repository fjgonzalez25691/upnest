# aws/lambdas/percentil/lambda_function.py

def lambda_handler(event, context):
    """
    Lambda handler to compute percentile for baby growth data.
    Expects event with: weight (kg), height (cm), age_months, sex ('male'/'female')
    """
    try:
        weight = float(event.get('weight'))
        height = float(event.get('height'))
        age_months = int(event.get('age_months'))
        sex = event.get('sex', 'male')

        # Dummy percentile logic for now (replace with real OMS formula later)
        # For example purposes, just returns median percentile
        percentile = 50

        return {
            "input": event,
            "percentile": percentile,
            "success": True
        }
    except Exception as e:
        return {
            "input": event,
            "error": str(e),
            "success": False
        }
