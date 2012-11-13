/******************************************************************************
 * home.js
 *
 * Implements JS for main vision board view
 ******************************************************************************/

/******************************************************************************
 * Utility functions
 */
function abort() {
  throw new Error("Abort");
}     
      
function AssertException(message) { this.message = message; }
  AssertException.prototype.toString = function () {
  return 'AssertException: ' + this.message;
} 

function assert(exp, message) {
  if (!exp) {
    throw new AssertException(message);
  }
}

function userLoggedIn() {
    return USER != null;
}

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
            HOME_GUEST: 1,
            HOME_USER: 2,
            USER_PROFILE: 3,
            INVALID: 4, // Keep at end: we use to check validity of pageMode
        },
    },
    // Variables in app
    Var: {
        JSON: null,
        PageStateModel: null,
        PageStateView: null,
        Model: null,
        View: null,
        Controller: null,
        Router: null,
    },
}

/******************************************************************************
 * Backbone models
 */

App.Backbone.Model.User = Backbone.Model.extend({

});

App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        visionId: -1,
        category: "",
        text: "",
        photoUrl: "",
        isPrivate: false,
        isGloballyShared: false,
        isFbShared: false,
        isSelected: false,
    },
    initialize: function() {
    },
    // Getters
    visionId: function() { return this.get("visionId"); },
    category: function() { return this.get("category"); },
    text: function() { return this.get("text"); },
    photoUrl: function() { return this.get("photoUrl"); },
    isPrivate: function() { return this.get("isPrivate"); },
    isGloballyShared: function() { return this.get("isGloballyShared"); },
    isFbShared: function() { return this.get("isFbShared"); },
    isSelected: function() { return this.get("isSelected"); },

    // Setters
    toggleSelected: function() {
        this.set({isSelected: !this.get("isSelected")});
    },
});

App.Backbone.Model.VisionList = Backbone.Collection.extend({
    model: App.Backbone.Model.Vision
});

App.Backbone.Model.VisionComment = Backbone.Model.extend({

});

App.Backbone.Model.Page = Backbone.Model.extend({
    defaults: {
        pageMode: App.Const.PageMode.HOME_LOADING,
        visionList: new App.Backbone.Model.VisionList(),
    },
    initialize: function() {
        this.set({
            visionList: new App.Backbone.Model.VisionList(
                                                        this.get("visionList")),
        });
    },
    // Getters
    pageMode: function() { return this.get("pageMode"); },
    visionList: function() { return this.get("visionList"); },

    // Setters
    setPageMode: function(mode) {
        assert(mode > 0 && mode < App.Const.PageMode.INVALID,
               "Invalid page mode");
        this.set({pageMode: mode});
    },
    setVisionList: function(visionList) {
        this.set({visionList: new App.Backbone.Model.VisionList(visionList) });
    },
});

/******************************************************************************
 * Backbone views
 */

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "div",
    className: "MasonryItem",
    initialize: function() {
        _.bindAll(this, "itemSelect");
        this.model.bind("change", this.render, this);
        this.render();
    },
    events: {
        "click .MasonryItemInner" : "itemSelect",
    },
    render: function() {
        var selectedClass = "MasonryItemUnselected";
        if (this.model.isSelected()) {
            selectedClass = "MasonryItemSelected";
        }
        var variables = {text : this.model.text(),
                         photoUrl: this.model.photoUrl(),
                         selected: selectedClass,
                        };

        if (this.model.photoUrl() == "") {
            var template = _.template($("#VisionTemplate").html(), variables);
            $(this.el).html(template);
        } else {
            var template = _.template($("#VisionImageTemplate").html(), variables);
            $(this.el).html(template);
        }

        return this;
    },
    itemSelect: function() {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.model.toggleSelected();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            $("#VisionDetailsModal").modal();
        } else {
            assert(false, "Invalid page mode in item select");
        }
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "changePageMode",
                        "renderVisionList",
                        "renderVision",
                        "showPageLoading",
                        "hidePageLoading",
                        "showInfoBar",
                        "hideInfoBar",
                        "showHome",
                        "renderHome",
                        "renderHomeError",
                        "showProfile",
                        "renderProfile",
                        "renderProfileError");
        this.model.bind("change:pageMode", this.changePageMode, this);
        this.model.bind("change:visionList", this.renderVisionList, this);
    },

    /*
     * Changing page mode triggered by set of this.model.pageMode
     */
    changePageMode: function() {
        console.log("CHANGE MODE: " + this.model.pageMode());

        var pageMode = this.model.pageMode();

        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.showInfoBar();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            this.hideInfoBar();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            this.showProfile();
        } else {
            assert(false, "Invalid page mode in changePageMode");
        }
    },

    /*
     * Render vision list: triggered by set of this.model.visionList
     */
    renderVisionList: function() {
        var masonryContainer = $("#MasonryContainer").first();

        masonryContainer.empty();
        this.children = []

        this.model.visionList().each(this.renderVision);

        masonryContainer.append(this.children);

        // TODO: Don't need to reload once we know heights of images
        masonryContainer.masonry({
            itemSelector: "div.MasonryItem",
            columnWidth:299
        }).imagesLoaded(function() {
            $("#MasonryContainer").masonry('reload');
        });
    },
    renderVision: function(vision, index) {
        var vision = new App.Backbone.View.Vision({ model: vision });
        this.children.push(vision.el);
    },

    /*
     * Show/hide notice of page loading
     */
    showPageLoading: function() {
        var masonryContainer = $("#MasonryContainer").first();
        masonryContainer.empty().masonry();

        var variables = {};
        var template = _.template($("#PageLoadingTemplate").html(), variables);
        $("#PageLoadingNotice").html(template).show();
    },
    hidePageLoading: function() {
        $("#PageLoadingNotice").hide();
    },

    /*
     * Show/hide information bar
     */
    showInfoBar: function() {
        $("#InfoContainer").show();
        $("#InfoContainerPadding").show();
    },
    hideInfoBar: function() {
        $("#InfoContainer").hide();
        $("#InfoContainerPadding").hide();
    },

    /*
     * Render home page
     */
    showHome: function() {
        this.showPageLoading();

        var ajaxUrl = "/api/get_main_page_visions";

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                App.Var.View.renderHomeError();
            },
            success: function(data, textStatus, jqXHR) {
                App.Var.JSON = data;
                App.Var.View.renderHome();
            }
        });
    },
    renderHome: function() {
        console.log("Render Home");
        this.hidePageLoading();
        this.model.setVisionList(App.Var.JSON.visionList);
    },
    renderHomeError: function() {
        var masonryContainer = $("#MasonryContainer").first();
        masonryContainer.empty().masonry();

        var variables = {};
        var template = _.template($("#HomePageLoadErrorTemplate").html(),
                                  variables);
        $("#PageLoadingNotice").html(template).show();
    },

    /*
     * Render user profile page
     */
    showProfile: function() {
        this.showPageLoading();
        this.hideInfoBar();

        var ajaxUrl = "/api/get_user_visions";

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                App.Var.View.renderProfileError();
            },
            success: function(data, textStatus, jqXHR) {
                App.Var.JSON = data;
                App.Var.View.renderProfile();
            }
        });
    },
    renderProfile: function() {
        console.log("Render Profile");
        this.hidePageLoading();
        this.model.setVisionList(App.Var.JSON.visionList);
    },
    renderProfileError: function() {
        var masonryContainer = $("#MasonryContainer").first();
        masonryContainer.empty().masonry();

        var variables = {};
        var template = _.template($("#ProfileLoadErrorTemplate").html(),
                                  variables);
        $("#PageLoadingNotice").html(template).show();
    },
});

/******************************************************************************
 * Router
 */
App.Backbone.Router = Backbone.Router.extend({
  routes: {
    ""                : "home",
    "profile"         : "profile",
    "*action"         : "home",
  },
  home: function() {
    if (userLoggedIn()) {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_USER);
    } else {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_GUEST);
    }
  },
  profile: function() {
    App.Var.Model.setPageMode(App.Const.PageMode.USER_PROFILE);
  },
});
App.Var.Router = new App.Backbone.Router();

/******************************************************************************
 * Document ready
 */
$(document).ready(function() {
    $.ajaxSetup({ cache: false});

    App.Var.Model = new App.Backbone.Model.Page();
    App.Var.View = new App.Backbone.View.Page({model: App.Var.Model});

    // Do this after we have created Page model and view
    Backbone.history.start({pushState: true});

    $("#NavHome").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/", {trigger: true});
    });
    $("#NavProfile").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/profile", {trigger: true});
    });

    $("#ReloadHome").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showHome();
    });
    $("#ReloadProfile").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showProfile();
    });
});

/* $eof */
