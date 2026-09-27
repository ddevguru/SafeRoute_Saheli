from flask import Blueprint, jsonify, render_template_string

docs_bp = Blueprint('docs', __name__)

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "SafeRoute Saheli API",
        "version": "1.0.0",
        "description": "Comprehensive REST and WebSocket API for the SafeRoute Saheli Women Safety Ecosystem (AI + IoT + Mobile + Cloud)."
    },
    "servers": [
        {"url": "http://127.0.0.1:5000", "description": "Local Development Server"},
        {"url": "https://api.saheli.org", "description": "Production Cloud Gateway"}
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "paths": {
        "/api/auth/register": {
            "post": {
                "summary": "Register new Saheli or Guardian",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string"},
                                    "phone": {"type": "string"},
                                    "password": {"type": "string"},
                                    "role": {"type": "string", "enum": ["SAHELI", "GUARDIAN"]}
                                }
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Registered successfully"}}
            }
        },
        "/api/auth/login": {
            "post": {
                "summary": "Authenticate user and receive JWT tokens",
                "tags": ["Authentication"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username_or_email": {"type": "string"},
                                    "password": {"type": "string"},
                                    "role": {"type": "string", "enum": ["SAHELI", "GUARDIAN"]}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "JWT tokens issued"}}
            }
        },
        "/api/emergency/trigger": {
            "post": {
                "summary": "Master emergency trigger (Mobile SOS button, ESP32 Touch, Clap, Fall)",
                "tags": ["Emergency"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "trigger_type": {"type": "string", "enum": ["TOUCH", "BUTTON", "VOICE", "CLAP", "MOTION_FALL", "MOTION_STRUGGLE"]},
                                    "latitude": {"type": "number"},
                                    "longitude": {"type": "number"},
                                    "device_id": {"type": "string"},
                                    "device_secret": {"type": "string"},
                                    "battery_percent": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Emergency incident created, FCM push sent, tracking link generated"}}
            }
        },
        "/api/emergency/{id}/cancel": {
            "post": {
                "summary": "De-escalate and resolve active emergency incident",
                "tags": ["Emergency"],
                "security": [{"BearerAuth": []}],
                "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Emergency incident marked CANCELLED/RESOLVED"}}
            }
        },
        "/api/location/update": {
            "post": {
                "summary": "Push real-time GPS coordinates from wearable or mobile",
                "tags": ["Live GPS"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "latitude": {"type": "number"},
                                    "longitude": {"type": "number"},
                                    "accuracy": {"type": "number"},
                                    "speed": {"type": "number"},
                                    "battery": {"type": "integer"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "GPS coordinate recorded & streamed via WebSocket"}}
            }
        },
        "/track/{token}": {
            "get": {
                "summary": "Public emergency tracking web viewer (No login required)",
                "tags": ["Live GPS"],
                "parameters": [{"name": "token", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "HTML Leaflet map interface"}}
            }
        },
        "/track/{token}/api": {
            "get": {
                "summary": "Real-time location polling JSON endpoint for public tracking page",
                "tags": ["Live GPS"],
                "parameters": [{"name": "token", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Live position, breadcrumb trail, battery, and incident status"}}
            }
        },
        "/api/camera/session": {
            "post": {
                "summary": "Generate signed ephemeral token to view live camera stream",
                "tags": ["ESP32-CAM"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "Signed token and stream URL returned"}}
            }
        },
        "/api/camera/capture": {
            "post": {
                "summary": "ESP32-CAM upload captured frame to forensics evidence vault",
                "tags": ["ESP32-CAM"],
                "responses": {"201": {"description": "Evidence photo hashed and stored"}}
            }
        },
        "/api/audio/analyze": {
            "post": {
                "summary": "Analyze acoustic stream or features for screams, cries, and distress",
                "tags": ["Audio AI"],
                "responses": {"200": {"description": "Acoustic classification result and confidence"}}
            }
        },
        "/api/audio/keyword": {
            "post": {
                "summary": "Voice keyword spotting for HELP, SAVE ME, BACHAO",
                "tags": ["Audio AI"],
                "responses": {"200": {"description": "Matched keyword and confidence score"}}
            }
        },
        "/api/nearby/all": {
            "get": {
                "summary": "Query all nearby verified Police, Hospitals, Shelters, and Pharmacies",
                "tags": ["Nearby Services"],
                "parameters": [
                    {"name": "lat", "in": "query", "schema": {"type": "number"}},
                    {"name": "lng", "in": "query", "schema": {"type": "number"}},
                    {"name": "radius_meters", "in": "query", "schema": {"type": "number"}}
                ],
                "responses": {"200": {"description": "Categorized places sorted by ascending distance"}}
            }
        },
        "/api/routes/calculate": {
            "post": {
                "summary": "Calculate AI Safe Routes comparing Safest, Balanced, and Fastest",
                "tags": ["Soft Computing Routing"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "3 optimized route alternatives with safety scores and waypoints"}}
            }
        },
        "/api/routes/deviation": {
            "post": {
                "summary": "Check real-time user cross-track distance against route deviation threshold",
                "tags": ["Soft Computing Routing"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "Deviation status and recommended action"}}
            }
        },
        "/api/admin/dashboard": {
            "get": {
                "summary": "Operations Command Center statistics and telemetry",
                "tags": ["Administration"],
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "Active emergencies, online devices, and user counts"}}
            }
        }
    }
}

@docs_bp.route('/api/openapi.json', methods=['GET'])
def get_openapi_json():
    """Serve OpenAPI 3.0 specification"""
    return jsonify(OPENAPI_SPEC), 200

@docs_bp.route('/api/docs', methods=['GET'])
@docs_bp.route('/docs', methods=['GET'])
def get_swagger_ui():
    """Interactive Swagger UI Documentation Page"""
    html_page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SafeRoute Saheli — Interactive API Documentation</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
        <style>
            body { margin: 0; padding: 0; background: #FAFAFA; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
            .topbar { background: #002350; padding: 14px 24px; color: #FFFFFF; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #D2AE39; }
            .topbar h1 { margin: 0; font-size: 20px; font-weight: 700; color: #D2AE39; }
            .topbar span { font-size: 13px; color: #A7F3D0; font-weight: 500; }
        </style>
    </head>
    <body>
        <div class="topbar">
            <h1>SafeRoute Saheli API Reference</h1>
            <span>OpenAPI 3.0 Interactive Console</span>
        </div>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/api/openapi.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout"
                });
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html_page)
