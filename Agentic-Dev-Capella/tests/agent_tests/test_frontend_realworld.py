"""
tests/agent_tests/test_frontend_realworld.py

Real-world frontend development test scenarios WITHOUT knowledge base dependency.
Tests standalone UI development capabilities for React, Vue, CSS, and accessibility agents.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.agent_tests.agent_test_framework import (
    AgentTestRunner,
    AgentTestSuite,
    create_validation_function
)


# ============================================================================
# UI DEVELOPER TESTS - Real-World Scenarios
# ============================================================================

def create_ui_developer_tests() -> AgentTestSuite:
    """
    Real-world UI component development tests.
    Tests standalone UI generation without legacy context.
    """
    suite = AgentTestSuite("ui_developer_agent")

    # Test 1: Build Dashboard Layout from Scratch
    suite.add_test(
        test_id="ui_001",
        test_name="Analytics Dashboard Layout - Greenfield",
        description="Build complete analytics dashboard with charts, tables, and filters",
        input_prompt="Create a responsive analytics dashboard with sidebar, header, and main content area",
        input_data={
            "framework": "react",
            "typescript": True,
            "page_type": "dashboard",
            "components": [
                {
                    "name": "DashboardLayout",
                    "type": "layout",
                    "sections": ["sidebar", "header", "main_content", "footer"]
                },
                {
                    "name": "MetricsCard",
                    "type": "component",
                    "props": ["title", "value", "change", "icon"]
                },
                {
                    "name": "ChartWidget",
                    "type": "component",
                    "chart_library": "recharts",
                    "chart_types": ["line", "bar", "pie"]
                },
                {
                    "name": "DataTable",
                    "type": "component",
                    "features": ["sorting", "filtering", "pagination", "row_selection"]
                },
                {
                    "name": "FilterPanel",
                    "type": "component",
                    "filters": ["date_range", "category", "status"]
                }
            ],
            "styling": "tailwind",
            "responsive": True,
            "dark_mode": True
        },
        expected_status="success",
        expected_fields=["code", "components", "styles", "dependencies"],
        validation_function=lambda r: {
            "valid": (
                "import React" in r.get("code", "") and
                "const DashboardLayout" in r.get("code", "") or "function DashboardLayout" in r.get("code", "") and
                "className" in r.get("code", "") and
                len(r.get("components", [])) >= 3
            ),
            "details": "Should contain React components with Tailwind styling"
        }
    )

    # Test 2: Build E-commerce Product Listing Page
    suite.add_test(
        test_id="ui_002",
        test_name="E-commerce Product Grid with Filters",
        description="Create product listing page with filtering, sorting, and cart",
        input_prompt="Build an e-commerce product listing page with filters and shopping cart",
        input_data={
            "framework": "react",
            "typescript": True,
            "components": [
                {
                    "name": "ProductGrid",
                    "type": "component",
                    "layout": "grid",
                    "responsive_cols": {"mobile": 1, "tablet": 2, "desktop": 4}
                },
                {
                    "name": "ProductCard",
                    "type": "component",
                    "features": ["image", "title", "price", "rating", "quick_view", "add_to_cart"]
                },
                {
                    "name": "FilterSidebar",
                    "type": "component",
                    "filters": [
                        {"type": "category", "multi_select": True},
                        {"type": "price_range", "slider": True},
                        {"type": "brand", "searchable": True},
                        {"type": "rating", "stars": True}
                    ]
                },
                {
                    "name": "SortDropdown",
                    "type": "component",
                    "options": ["price_low_to_high", "price_high_to_low", "newest", "most_popular"]
                },
                {
                    "name": "ShoppingCart",
                    "type": "component",
                    "features": ["quantity_controls", "remove_item", "total_calculation", "checkout_button"]
                }
            ],
            "state_management": "zustand",
            "styling": "css_modules",
            "image_optimization": True,
            "lazy_loading": True
        },
        expected_status="success",
        expected_fields=["code", "components", "state_management_code", "styles"],
        validation_function=lambda r: {
            "valid": (
                "ProductGrid" in r.get("code", "") and
                "ProductCard" in r.get("code", "") and
                ("useState" in r.get("code", "") or "zustand" in r.get("state_management_code", "")) and
                len(r.get("components", [])) >= 4
            ),
            "details": "Should include product grid, cards, filters, and state management"
        }
    )

    # Test 3: Build Authentication Flow (Login, Signup, Reset Password)
    suite.add_test(
        test_id="ui_003",
        test_name="Authentication Flow - Complete UI",
        description="Build complete authentication UI with validation and error handling",
        input_prompt="Create authentication pages: login, signup, forgot password, and reset password",
        input_data={
            "framework": "react",
            "typescript": True,
            "pages": [
                {
                    "name": "LoginPage",
                    "fields": ["email", "password"],
                    "features": ["remember_me", "social_login", "forgot_password_link"]
                },
                {
                    "name": "SignupPage",
                    "fields": ["name", "email", "password", "confirm_password"],
                    "features": ["terms_checkbox", "password_strength_indicator"]
                },
                {
                    "name": "ForgotPasswordPage",
                    "fields": ["email"],
                    "features": ["success_message"]
                },
                {
                    "name": "ResetPasswordPage",
                    "fields": ["new_password", "confirm_password"],
                    "features": ["password_requirements", "success_redirect"]
                }
            ],
            "validation": "react_hook_form",
            "styling": "styled_components",
            "error_handling": True,
            "loading_states": True,
            "responsive": True
        },
        expected_status="success",
        expected_fields=["code", "pages", "validation_schemas", "styles"],
        validation_function=lambda r: {
            "valid": (
                "LoginPage" in r.get("code", "") and
                "SignupPage" in r.get("code", "") and
                ("useForm" in r.get("code", "") or len(r.get("validation_schemas", "")) > 0) and
                len(r.get("pages", [])) >= 3
            ),
            "details": "Should include all auth pages with form validation"
        }
    )

    # Test 4: Build Real-time Chat Interface
    suite.add_test(
        test_id="ui_004",
        test_name="Real-time Chat Interface with WebSocket",
        description="Create chat UI with message list, input, typing indicators, and online status",
        input_prompt="Build a real-time chat interface with WebSocket integration",
        input_data={
            "framework": "react",
            "typescript": True,
            "components": [
                {
                    "name": "ChatContainer",
                    "type": "layout",
                    "sections": ["conversation_list", "message_area", "user_profile"]
                },
                {
                    "name": "ConversationList",
                    "type": "component",
                    "features": ["search", "unread_count", "last_message_preview", "online_status"]
                },
                {
                    "name": "MessageArea",
                    "type": "component",
                    "features": ["message_list", "date_separators", "typing_indicator", "read_receipts"]
                },
                {
                    "name": "MessageBubble",
                    "type": "component",
                    "features": ["timestamp", "sender_avatar", "message_status", "reactions"]
                },
                {
                    "name": "MessageInput",
                    "type": "component",
                    "features": ["emoji_picker", "file_upload", "send_button", "typing_detection"]
                }
            ],
            "websocket": "socket.io-client",
            "styling": "tailwind",
            "optimistic_ui_updates": True,
            "infinite_scroll": True
        },
        expected_status="success",
        expected_fields=["code", "components", "websocket_integration", "styles"],
        validation_function=lambda r: {
            "valid": (
                "ChatContainer" in r.get("code", "") and
                "MessageBubble" in r.get("code", "") and
                ("socket" in r.get("websocket_integration", "").lower() or "websocket" in r.get("code", "").lower()) and
                len(r.get("components", [])) >= 4
            ),
            "details": "Should include chat components with WebSocket integration"
        }
    )

    # Test 5: Build Data Visualization Dashboard
    suite.add_test(
        test_id="ui_005",
        test_name="Data Visualization Dashboard with Interactive Charts",
        description="Create dashboard with multiple interactive charts and real-time updates",
        input_prompt="Build a data visualization dashboard with interactive charts",
        input_data={
            "framework": "react",
            "typescript": True,
            "components": [
                {
                    "name": "LineChart",
                    "type": "chart",
                    "library": "recharts",
                    "features": ["tooltip", "legend", "zoom", "brush"]
                },
                {
                    "name": "BarChart",
                    "type": "chart",
                    "library": "recharts",
                    "features": ["stacked", "grouped", "horizontal"]
                },
                {
                    "name": "PieChart",
                    "type": "chart",
                    "library": "recharts",
                    "features": ["donut", "labels", "custom_colors"]
                },
                {
                    "name": "HeatMap",
                    "type": "chart",
                    "library": "recharts",
                    "features": ["color_scale", "cell_labels"]
                },
                {
                    "name": "KPICard",
                    "type": "component",
                    "features": ["value", "trend", "sparkline", "comparison"]
                }
            ],
            "real_time_updates": True,
            "export_options": ["png", "csv", "pdf"],
            "responsive": True,
            "styling": "tailwind"
        },
        expected_status="success",
        expected_fields=["code", "components", "chart_configurations", "export_handlers"],
        validation_function=lambda r: {
            "valid": (
                "LineChart" in r.get("code", "") or "BarChart" in r.get("code", "") and
                "recharts" in str(r.get("code", "")).lower() and
                len(r.get("components", [])) >= 4 and
                len(r.get("chart_configurations", [])) > 0
            ),
            "details": "Should include multiple chart types with configurations"
        }
    )

    return suite


# ============================================================================
# REACT SPECIALIST TESTS - Advanced React Patterns
# ============================================================================

def create_react_specialist_tests() -> AgentTestSuite:
    """
    Advanced React development tests with hooks, context, and performance optimization.
    """
    suite = AgentTestSuite("react_specialist_agent")

    # Test 1: Build Complex Form with Multi-Step Wizard
    suite.add_test(
        test_id="react_001",
        test_name="Multi-Step Form Wizard with Validation",
        description="Create multi-step form wizard with step navigation and validation",
        input_prompt="Build a multi-step form wizard for user onboarding",
        input_data={
            "steps": [
                {
                    "name": "personal_info",
                    "title": "Personal Information",
                    "fields": ["first_name", "last_name", "email", "phone"]
                },
                {
                    "name": "company_info",
                    "title": "Company Information",
                    "fields": ["company_name", "industry", "company_size", "role"]
                },
                {
                    "name": "preferences",
                    "title": "Preferences",
                    "fields": ["notifications", "newsletter", "language", "timezone"]
                },
                {
                    "name": "review",
                    "title": "Review & Submit",
                    "type": "summary"
                }
            ],
            "validation": "yup",
            "features": [
                "step_navigation",
                "progress_indicator",
                "save_draft",
                "back_button",
                "field_validation",
                "step_validation"
            ],
            "state_management": "context_api",
            "typescript": True
        },
        expected_status="success",
        expected_fields=["code", "validation_schemas", "context_provider", "custom_hooks"],
        validation_function=lambda r: {
            "valid": (
                "useState" in r.get("code", "") and
                "useContext" in r.get("code", "") or len(r.get("context_provider", "")) > 0 and
                len(r.get("validation_schemas", "")) > 0 and
                len(r.get("custom_hooks", [])) > 0
            ),
            "details": "Should use React hooks, Context API, and validation schemas"
        }
    )

    # Test 2: Build Infinite Scroll Feed with Virtualization
    suite.add_test(
        test_id="react_002",
        test_name": "Infinite Scroll Feed with Virtual Scrolling",
        description="Create performant infinite scroll feed with react-window",
        input_prompt="Build an infinite scroll social media feed with virtualization",
        input_data={
            "component_name": "InfiniteFeed",
            "item_type": "social_post",
            "features": [
                "infinite_scroll",
                "virtual_scrolling",
                "pull_to_refresh",
                "skeleton_loading",
                "error_retry",
                "empty_state"
            ],
            "virtualization_library": "react-window",
            "data_fetching": "react-query",
            "item_height": "variable",
            "typescript": True
        },
        expected_status="success",
        expected_fields=["code", "custom_hooks", "performance_optimizations"],
        validation_function=lambda r: {
            "valid": (
                ("react-window" in r.get("code", "") or "VariableSizeList" in r.get("code", "")) and
                ("useInfiniteQuery" in r.get("code", "") or "react-query" in r.get("code", "")) and
                len(r.get("performance_optimizations", [])) > 0
            ),
            "details": "Should use react-window for virtualization and react-query for data fetching"
        }
    )

    # Test 3: Build Drag-and-Drop Kanban Board
    suite.add_test(
        test_id="react_003",
        test_name="Drag-and-Drop Kanban Board",
        description="Create interactive Kanban board with drag-and-drop functionality",
        input_prompt="Build a Kanban board with drag-and-drop between columns",
        input_data={
            "component_name": "KanbanBoard",
            "columns": ["To Do", "In Progress", "Review", "Done"],
            "card_fields": ["title", "description", "assignee", "priority", "due_date", "tags"],
            "features": [
                "drag_drop_cards",
                "drag_drop_columns",
                "add_card",
                "edit_card",
                "delete_card",
                "filter_by_assignee",
                "search_cards"
            ],
            "dnd_library": "react-beautiful-dnd",
            "state_management": "redux_toolkit",
            "typescript": True,
            "responsive": True
        },
        expected_status="success",
        expected_fields=["code", "redux_slices", "dnd_handlers", "components"],
        validation_function=lambda r: {
            "valid": (
                ("DragDropContext" in r.get("code", "") or "dnd" in r.get("code", "").lower()) and
                (len(r.get("redux_slices", [])) > 0 or "createSlice" in r.get("code", "")) and
                len(r.get("dnd_handlers", [])) > 0
            ),
            "details": "Should include drag-and-drop functionality and Redux state management"
        }
    )

    # Test 4: Build Real-time Collaborative Editor
    suite.add_test(
        test_id="react_004",
        test_name="Real-time Collaborative Rich Text Editor",
        description="Create collaborative editor with real-time synchronization",
        input_prompt="Build a real-time collaborative rich text editor",
        input_data={
            "editor_library": "slate",
            "features": [
                "bold",
                "italic",
                "underline",
                "headings",
                "lists",
                "links",
                "images",
                "code_blocks",
                "mentions",
                "comments"
            ],
            "collaboration": {
                "backend": "websocket",
                "conflict_resolution": "operational_transformation",
                "cursor_sharing": True,
                "user_presence": True
            },
            "autosave": True,
            "version_history": True,
            "typescript": True
        },
        expected_status="success",
        expected_fields=["code", "editor_plugins", "websocket_handlers", "ot_implementation"],
        validation_function=lambda r: {
            "valid": (
                "slate" in r.get("code", "").lower() and
                len(r.get("editor_plugins", [])) > 0 and
                ("websocket" in str(r.get("websocket_handlers", "")).lower() or "socket" in r.get("code", "").lower())
            ),
            "details": "Should use Slate editor with WebSocket for collaboration"
        }
    )

    # Test 5: Build Advanced Data Grid with Server-Side Operations
    suite.add_test(
        test_id="react_005",
        test_name="Advanced Data Grid with Server-Side Pagination",
        description="Create feature-rich data grid with server-side pagination, sorting, filtering",
        input_prompt="Build an advanced data grid with server-side operations",
        input_data={
            "library": "ag-grid-react",
            "features": [
                "server_side_pagination",
                "server_side_sorting",
                "server_side_filtering",
                "column_resizing",
                "column_reordering",
                "column_pinning",
                "row_selection",
                "cell_editing",
                "export_to_csv",
                "custom_cell_renderers"
            ],
            "total_rows": "1M+",
            "api_integration": True,
            "caching": "react-query",
            "typescript": True
        },
        expected_status="success",
        expected_fields=["code", "column_definitions", "api_handlers", "custom_renderers"],
        validation_function=lambda r: {
            "valid": (
                "ag-grid" in r.get("code", "").lower() and
                len(r.get("column_definitions", [])) > 0 and
                len(r.get("api_handlers", [])) > 0
            ),
            "details": "Should use AG Grid with server-side data model"
        }
    )

    return suite


# ============================================================================
# CSS SPECIALIST TESTS - Advanced Styling and Animations
# ============================================================================

def create_css_specialist_tests() -> AgentTestSuite:
    """
    Advanced CSS tests with animations, responsive design, and modern techniques.
    """
    suite = AgentTestSuite("css_specialist_agent")

    # Test 1: Build Responsive Landing Page
    suite.add_test(
        test_id="css_001",
        test_name="Modern Responsive Landing Page",
        description="Create responsive landing page with hero, features, and CTA sections",
        input_prompt="Build a modern responsive landing page with smooth animations",
        input_data={
            "sections": [
                {
                    "name": "hero",
                    "layout": "split",
                    "content": ["heading", "subheading", "cta_buttons", "hero_image"],
                    "animation": "fade_in_up"
                },
                {
                    "name": "features",
                    "layout": "grid_3_columns",
                    "content": ["icon", "title", "description"],
                    "animation": "stagger_fade_in"
                },
                {
                    "name": "testimonials",
                    "layout": "carousel",
                    "content": ["quote", "author", "avatar", "rating"],
                    "animation": "slide"
                },
                {
                    "name": "pricing",
                    "layout": "card_grid",
                    "content": ["plan_name", "price", "features_list", "cta_button"],
                    "animation": "scale_on_hover"
                },
                {
                    "name": "cta_footer",
                    "layout": "centered",
                    "content": ["heading", "email_input", "submit_button"],
                    "animation": "none"
                }
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px", "wide": "1440px"},
            "approach": "mobile_first",
            "css_framework": "tailwind",
            "animations": "framer_motion",
            "dark_mode": True
        },
        expected_status="success",
        expected_fields=["html", "css", "animations", "responsive_classes"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("css", "")) > 0 and
                ("@media" in r.get("css", "") or "sm:" in r.get("responsive_classes", "")) and
                len(r.get("animations", [])) > 0
            ),
            "details": "Should include responsive CSS and animations"
        }
    )

    # Test 2: Build CSS Grid Complex Layout
    suite.add_test(
        test_id="css_002",
        test_name="Magazine-Style CSS Grid Layout",
        description="Create complex magazine layout using CSS Grid",
        input_prompt="Build a magazine-style layout with CSS Grid",
        input_data={
            "layout_type": "magazine",
            "grid_areas": [
                "header (full width)",
                "featured_article (2/3 width)",
                "sidebar (1/3 width)",
                "article_grid (4 columns)",
                "newsletter (full width)",
                "footer (3 columns)"
            ],
            "features": [
                "responsive_grid",
                "masonry_layout",
                "sticky_sidebar",
                "parallax_images"
            ],
            "breakpoints": {"mobile": "1fr", "tablet": "repeat(2, 1fr)", "desktop": "repeat(4, 1fr)"},
            "approach": "css_grid_native"
        },
        expected_status="success",
        expected_fields=["css", "grid_templates", "media_queries"],
        validation_function=lambda r: {
            "valid": (
                "display: grid" in r.get("css", "") and
                "grid-template" in r.get("css", "") and
                len(r.get("media_queries", [])) >= 2
            ),
            "details": "Should use CSS Grid with responsive breakpoints"
        }
    )

    # Test 3: Build Advanced Animations and Transitions
    suite.add_test(
        test_id="css_003",
        test_name="Advanced UI Animations Library",
        description="Create reusable animation library with keyframes and transitions",
        input_prompt="Build a library of reusable CSS animations",
        input_data={
            "animations": [
                {"name": "fade_in", "type": "entrance", "duration": "0.3s"},
                {"name": "slide_in_from_left", "type": "entrance", "duration": "0.5s"},
                {"name": "bounce", "type": "attention", "duration": "0.6s"},
                {"name": "shake", "type": "attention", "duration": "0.5s"},
                {"name": "pulse", "type": "attention", "duration": "1s", "infinite": True},
                {"name": "rotate_360", "type": "custom", "duration": "1s"},
                {"name": "morph", "type": "transition", "duration": "0.4s"},
                {"name": "flip", "type": "3d", "duration": "0.6s"}
            ],
            "easing_functions": ["ease", "ease-in-out", "cubic-bezier"],
            "include_hover_effects": True,
            "include_loading_animations": True,
            "approach": "css_only"
        },
        expected_status="success",
        expected_fields=["css", "keyframes", "utility_classes"],
        validation_function=lambda r: {
            "valid": (
                "@keyframes" in r.get("css", "") and
                "animation" in r.get("css", "") and
                len(r.get("keyframes", [])) >= 5
            ),
            "details": "Should include multiple @keyframes animations"
        }
    )

    # Test 4: Build Dark Mode Theme System
    suite.add_test(
        test_id="css_004",
        test_name="Complete Dark Mode Theme System",
        description="Create comprehensive dark mode with CSS custom properties",
        input_prompt="Build a dark mode theme system with smooth transitions",
        input_data={
            "approach": "css_variables",
            "color_scheme": {
                "light": {
                    "primary": "#3B82F6",
                    "background": "#FFFFFF",
                    "surface": "#F3F4F6",
                    "text": "#1F2937",
                    "text_secondary": "#6B7280"
                },
                "dark": {
                    "primary": "#60A5FA",
                    "background": "#111827",
                    "surface": "#1F2937",
                    "text": "#F9FAFB",
                    "text_secondary": "#D1D5DB"
                }
            },
            "features": [
                "theme_toggle",
                "system_preference_detection",
                "local_storage_persistence",
                "smooth_transition",
                "component_theming"
            ],
            "transition_duration": "0.3s"
        },
        expected_status="success",
        expected_fields=["css", "css_variables", "theme_toggle_code"],
        validation_function=lambda r: {
            "valid": (
                "--" in r.get("css", "") and
                "prefers-color-scheme" in r.get("css", "") and
                len(r.get("css_variables", {})) > 0
            ),
            "details": "Should use CSS custom properties and prefers-color-scheme"
        }
    )

    # Test 5: Build Glassmorphism UI Components
    suite.add_test(
        test_id="css_005",
        test_name="Glassmorphism UI Component Library",
        description="Create modern glassmorphism components with backdrop filters",
        input_prompt="Build glassmorphism UI components (cards, modals, navigation)",
        input_data={
            "components": [
                "glass_card",
                "glass_modal",
                "glass_navigation",
                "glass_sidebar",
                "glass_button",
                "glass_input"
            ],
            "style": {
                "blur": "10px",
                "opacity": "0.8",
                "border": "1px solid rgba(255,255,255,0.2)",
                "shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.37)"
            },
            "include_hover_effects": True,
            "include_active_states": True,
            "responsive": True
        },
        expected_status="success",
        expected_fields=["css", "component_styles", "utility_classes"],
        validation_function=lambda r: {
            "valid": (
                "backdrop-filter" in r.get("css", "") and
                "blur" in r.get("css", "") and
                len(r.get("component_styles", {})) >= 4
            ),
            "details": "Should use backdrop-filter for glassmorphism effect"
        }
    )

    return suite


# ============================================================================
# ACCESSIBILITY SPECIALIST TESTS - WCAG Compliance
# ============================================================================

def create_accessibility_specialist_tests() -> AgentTestSuite:
    """
    Accessibility testing for WCAG 2.1 AA/AAA compliance.
    """
    suite = AgentTestSuite("accessibility_specialist_agent")

    # Test 1: Make E-commerce Site WCAG 2.1 AA Compliant
    suite.add_test(
        test_id="a11y_001",
        test_name="E-commerce WCAG 2.1 AA Compliance",
        description="Audit and fix e-commerce site for WCAG 2.1 AA compliance",
        input_prompt="Make e-commerce product listing page WCAG 2.1 AA compliant",
        input_data={
            "page_type": "product_listing",
            "components": [
                "product_cards",
                "filter_sidebar",
                "search_bar",
                "shopping_cart",
                "navigation_menu"
            ],
            "wcag_level": "AA",
            "focus_areas": [
                "keyboard_navigation",
                "screen_reader_support",
                "color_contrast",
                "focus_indicators",
                "aria_labels",
                "semantic_html"
            ],
            "include_fixes": True,
            "include_testing_guide": True
        },
        expected_status="success",
        expected_fields=["accessibility_report", "code_fixes", "aria_attributes", "testing_guide"],
        validation_function=lambda r: {
            "valid": (
                len(r.get("accessibility_report", {})) > 0 and
                len(r.get("code_fixes", [])) > 0 and
                len(r.get("aria_attributes", [])) > 0
            ),
            "details": "Should include accessibility audit report and code fixes"
        }
    )

    # Test 2: Build Accessible Form with Complex Validation
    suite.add_test(
        test_id="a11y_002",
        test_name="Fully Accessible Multi-Step Form",
        description="Create accessible multi-step form with live validation feedback",
        input_prompt="Build an accessible multi-step form with screen reader support",
        input_data={
            "form_type": "multi_step_registration",
            "steps": 4,
            "field_types": [
                "text_input",
                "email",
                "password",
                "select_dropdown",
                "radio_buttons",
                "checkboxes",
                "file_upload",
                "date_picker"
            ],
            "accessibility_features": [
                "aria_live_regions",
                "error_announcements",
                "required_field_indicators",
                "field_descriptions",
                "keyboard_navigation",
                "focus_management",
                "progress_announcement"
            ],
            "framework": "react",
            "typescript": True
        },
        expected_status="success",
        expected_fields=["code", "aria_implementation", "keyboard_handlers", "screen_reader_text"],
        validation_function=lambda r: {
            "valid": (
                "aria-" in r.get("code", "") and
                "role=" in r.get("code", "") and
                len(r.get("aria_implementation", {})) > 0 and
                len(r.get("keyboard_handlers", [])) > 0
            ),
            "details": "Should include ARIA attributes and keyboard handlers"
        }
    )

    # Test 3: Build Accessible Data Table
    suite.add_test(
        test_id="a11y_003",
        test_name="Accessible Complex Data Table",
        description="Create accessible data table with sorting, filtering, and pagination",
        input_prompt="Build an accessible data table with advanced features",
        input_data={
            "table_type": "data_grid",
            "features": [
                "sortable_columns",
                "filterable_columns",
                "pagination",
                "row_selection",
                "expandable_rows"
            ],
            "accessibility_requirements": [
                "table_headers_association",
                "sort_direction_announcement",
                "row_count_announcement",
                "keyboard_navigation",
                "focus_visible",
                "aria_describedby"
            ],
            "rows": "100+",
            "columns": 8
        },
        expected_status="success",
        expected_fields=["code", "table_markup", "aria_labels", "keyboard_navigation"],
        validation_function=lambda r: {
            "valid": (
                "<table" in r.get("table_markup", "") and
                "scope=" in r.get("table_markup", "") and
                len(r.get("aria_labels", [])) > 0 and
                len(r.get("keyboard_navigation", {})) > 0
            ),
            "details": "Should use semantic table markup with proper ARIA"
        }
    )

    # Test 4: Build Accessible Modal and Dialog System
    suite.add_test(
        test_id="a11y_004",
        test_name="Accessible Modal and Dialog System",
        description="Create accessible modals with focus trapping and screen reader support",
        input_prompt="Build accessible modals and dialogs with proper focus management",
        input_data={
            "modal_types": [
                "alert_dialog",
                "confirmation_dialog",
                "form_modal",
                "full_screen_modal"
            ],
            "accessibility_features": [
                "focus_trap",
                "escape_to_close",
                "return_focus_on_close",
                "aria_modal",
                "aria_labelledby",
                "backdrop_click_close",
                "initial_focus_management"
            ],
            "framework": "react",
            "include_animations": True
        },
        expected_status="success",
        expected_fields=["code", "focus_trap_implementation", "aria_attributes", "keyboard_handlers"],
        validation_function=lambda r: {
            "valid": (
                "aria-modal" in r.get("code", "") or "aria-modal" in str(r.get("aria_attributes", [])) and
                ("focus" in r.get("focus_trap_implementation", "").lower()) and
                ("Escape" in str(r.get("keyboard_handlers", [])) or "Escape" in r.get("code", ""))
            ),
            "details": "Should include focus trap and ARIA modal attributes"
        }
    )

    # Test 5: Build Accessible Media Player
    suite.add_test(
        test_id="a11y_005",
        test_name="Fully Accessible Video Player",
        description="Create accessible video player with captions, transcripts, and keyboard controls",
        input_prompt="Build an accessible video player with full keyboard support",
        input_data={
            "player_type": "video",
            "features": [
                "play_pause",
                "seek_bar",
                "volume_control",
                "fullscreen",
                "playback_speed",
                "captions_toggle",
                "audio_descriptions"
            ],
            "accessibility_features": [
                "keyboard_controls",
                "captions_and_subtitles",
                "transcript",
                "screen_reader_announcements",
                "focus_indicators",
                "aria_live_regions",
                "custom_controls"
            ],
            "caption_formats": ["vtt", "srt"],
            "framework": "react"
        },
        expected_status="success",
        expected_fields=["code", "keyboard_shortcuts", "caption_implementation", "aria_live"],
        validation_function=lambda r: {
            "valid": (
                "video" in r.get("code", "") or "<video" in r.get("code", "") and
                len(r.get("keyboard_shortcuts", {})) >= 5 and
                ("track" in r.get("caption_implementation", "") or "captions" in r.get("code", "").lower())
            ),
            "details": "Should include video element with captions and keyboard controls"
        }
    )

    return suite


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_frontend_realworld_tests(agent_name: str = "all", save_results: bool = True):
    """
    Run real-world frontend development tests.

    Args:
        agent_name: Name of agent to test or "all"
        save_results: Whether to save results to file
    """
    # Import Phase 2 agents
    try:
        from agents.frontend.ui_developer.agent import UIDevAgent
        from agents.frontend.react_specialist.agent import ReactSpecialistAgent
        from agents.frontend.css_specialist.agent import CSSSpecialistAgent
        from agents.frontend.accessibility_specialist.agent import AccessibilitySpecialistAgent

        # Create standalone agent instances (no message bus for testing)
        ui_agent = UIDevAgent(context={}, message_bus=None, orchestrator_id="test_orch")
        react_agent = ReactSpecialistAgent(context={}, message_bus=None, orchestrator_id="test_orch")
        css_agent = CSSSpecialistAgent(context={}, message_bus=None, orchestrator_id="test_orch")
        a11y_agent = AccessibilitySpecialistAgent(context={}, message_bus=None, orchestrator_id="test_orch")

        test_suites = {
            "ui_developer_agent": (create_ui_developer_tests, ui_agent),
            "react_specialist_agent": (create_react_specialist_tests, react_agent),
            "css_specialist_agent": (create_css_specialist_tests, css_agent),
            "accessibility_specialist_agent": (create_accessibility_specialist_tests, a11y_agent),
        }

    except ImportError as e:
        print(f"Error importing Phase 2 frontend agents: {e}")
        print("Make sure agents/frontend/* agents are implemented.")
        return

    if agent_name == "all":
        agents_to_test = list(test_suites.keys())
    elif agent_name in test_suites:
        agents_to_test = [agent_name]
    else:
        print(f"Error: Unknown agent '{agent_name}'")
        print(f"Available agents: {', '.join(['all'] + list(test_suites.keys()))}")
        return

    all_summaries = []

    print("\n" + "="*80)
    print("REAL-WORLD FRONTEND DEVELOPMENT TESTS (No Knowledge Base)")
    print("="*80)

    for agent in agents_to_test:
        suite_creator, agent_instance = test_suites[agent]
        suite = suite_creator()

        # Create test runner
        runner = AgentTestRunner(agent_instance, agent)

        # Run tests
        summary = runner.run_test_suite(suite.get_test_cases())
        all_summaries.append(summary)

        # Save results
        if save_results:
            output_path = f"tests/agent_tests/results/{agent}_realworld_results.json"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            runner.save_results(output_path)

    # Print overall summary
    if len(all_summaries) > 1:
        print("\n" + "="*80)
        print("OVERALL TEST SUMMARY")
        print("="*80)

        total_tests = sum(s["total_tests"] for s in all_summaries)
        total_passed = sum(s["passed"] for s in all_summaries)
        total_failed = sum(s["failed"] for s in all_summaries)
        total_errors = sum(s["errors"] for s in all_summaries)

        print(f"Total Agents Tested: {len(all_summaries)}")
        print(f"Total Tests:         {total_tests}")
        print(f"✓ Passed:            {total_passed}")
        print(f"✗ Failed:            {total_failed}")
        print(f"⚠ Errors:            {total_errors}")
        print(f"Success Rate:        {(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        print("="*80)

    return all_summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test frontend agents with real-world scenarios")
    parser.add_argument(
        "--agent",
        default="all",
        help="Agent to test: ui_developer_agent, react_specialist_agent, css_specialist_agent, accessibility_specialist_agent, or all"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()
    run_frontend_realworld_tests(agent_name=args.agent, save_results=not args.no_save)
