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

            GUEST_PROFILE: 5,
            INVALID: 6, // Keep at end: we use to check validity of pageMode
        },
        VisionPrivacy: {
            PRIVATE: 1,
            PUBLIC: 2,
        },
        MAX_SELECTED_VISIONS: 10,
    },
    // Variables in app
    Var: {
        JSON: null,
        Model: null,
        View: null,
        Router: null,
    },
}

