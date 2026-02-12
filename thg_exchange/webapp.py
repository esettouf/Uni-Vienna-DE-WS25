# Entry point for the application.

from flask import request, jsonify

from thg_exchange.graphql_schema import schema
from thg_exchange import app
from thg_exchange.auth_utils import decode_token

# GraphQL POST Route to execute schema
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json(force=True)

    # Extract JWT if present
    auth_header = request.headers.get("Authorization", "")
    user_context = {}
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            user_context = {
                "user_id": payload.get("sub"),
                "role": payload.get("role"),
            }
        except Exception:
            # Invalid/expired token; continue without user context
            user_context = {}

    result = schema.execute(
        data.get("query"),
        variable_values=data.get("variables"),
        operation_name=data.get("operationName"),
        context_value=user_context,
    )

    # Manually formatted JSON payload from Graphene ExecutionResult
    errors = result.errors and [getattr(e, "formatted", None) or {"message": str(e)} for e in result.errors]
    return jsonify({"data": result.data, **({"errors": errors} if errors else {})}), (200 if not errors else 400)


# Define Flask port to run on
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
