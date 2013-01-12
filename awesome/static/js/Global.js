/******************************************************************************
 * Constants
 */

/******************************************************************************
 * Namespace
 */
var App = {
    // Namespace for Backbone data structures
    Backbone: {
        Model: {},
        View: {},
        Router: null,
    },
    Const: {
        PageMode: {
            EMPTY: 0,
            //Main Page (not logged in)
            HOME_GUEST: 1, 
            //Main Page (logged in)
            HOME_USER: 2,
            //Example vision board (not logged in)
            EXAMPLE_VISION_BOARD: 3,
            //User Page (logged in)
            USER_PROFILE: 4,
            //Vision details modal
            VISION_DETAILS: 5,
            //Vision details full page (if we came directly here)
            VISION_PAGE: 6,

            GUEST_PROFILE: 7,
            INVALID: 8, // Keep at end: we use to check validity of pageMode
        },
        VisionPrivacy: {
            PRIVATE: 0,
            PUBLIC: 1,
        },
        MAX_SELECTED_VISIONS: 10,

        /* Page Options */
        Options: {
            NONE: 0,
            ONBOARDING: 1
        },

        Strings: {
            COMMENT_PROMPT_FRIEND: "Any thoughts about this?",
            COMMENT_PROMPT_OWN: "Any progress?"
        }
    },
    // Variables in app
    Var: {
        JSON: null,
        Model: null,
        View: null,
        Router: null,
    },
}

