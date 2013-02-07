/******************************************************************************
 * Router
 */
App.Backbone.Router = Backbone.Router.extend({
  routes: {
    ""                          : "home",
    "recent"                    : "recent",
    "view_board"                : "viewBoard",
    "user/:userId"              : "profile",
    "welcome"                   : "welcome",
    "vision/:visionId"          : "vision",
    "*action"                   : "home",
  },

  home: function() {
    if (userLoggedIn()) {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_USER);
    } else {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_GUEST);
    }
  },
  recent: function() {
    if (userLoggedIn()) {
        App.Var.Model.setPageMode(App.Const.PageMode.FEED);
    } else {
        console.log("here");
        assert(False, "Should be logged in to go to feed");
    }
  },
  viewBoard: function() {
      if (!userLoggedIn() &&
          (App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST ||
           App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE)) {
        App.Var.Model.setPageMode(App.Const.PageMode.EXAMPLE_VISION_BOARD);
      } else {
        assert(false, "Shouldn't be logged in or come from another page");
      }
  },
  profile: function(userId) {
    App.Var.Model.setCurrentUserId(userId);
    App.Var.Model.setPageMode(App.Const.PageMode.USER_PROFILE);
  },
  

  welcome: function() {
    //Set Profile
    this.home();
    App.Var.Model.setOption(App.Const.Options.ONBOARDING);
  },
  
  vision: function(visionId) {
    if (App.Var.Model.currentVision() != null) {
      App.Var.Model.setPageMode(App.Const.PageMode.VISION_DETAILS);
    } else {
        if (userLoggedIn()) {
            currentVisionId = visionId;
            App.Var.Model.setPageMode(App.Const.PageMode.VISION_PAGE);
        } else {
            window.location("/login");
        }
    }
  },
});

// Should be called after routes are defined
App.Var.Router = new App.Backbone.Router();

