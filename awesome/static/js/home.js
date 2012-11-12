/******************************************************************************
 * home.js
 *
 * Implements JS for main vision board view
 ******************************************************************************/

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
    // Variables in app
    Var: {
        JSON: null,
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
        visionList: new App.Backbone.Model.VisionList(),
    },
    initialize: function() {
        this.set({
            visionList: new App.Backbone.Model.VisionList(this.get("visionList")),
        });
    },
    visionList: function() { return this.get("visionList"); },
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
                         selectedClass: selectedClass,
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
        console.log("CLICK");
        this.model.toggleSelected();
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "renderVisionList", "renderVision");
        this.render();
    },
    render: function() {
        if (this.options.loading == false && this.options.loadError == false) {
            console.log("Render Vision list");
            this.renderVisionList();
        }
    },
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
});

/******************************************************************************
 * Controller
 */

App.Var.Controller = {
    initialize: function() {
        Backbone.history.start({pushState: true});
    },
    showHome: function() {
        var ajaxUrl = "/api/get_test_vision_list";

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
                App.Var.Controller.renderPageLoading();
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                App.Var.Controller.renderHomeError();
            },
            success: function(data, textStatus, jqXHR) {
                //console.log("DATA: " + JSON.stringify(data));
                App.Var.JSON = data;
                App.Var.Controller.renderHome();
            }
        });
    },
    renderHome: function() {
        console.log("Render Home");
        App.Var.Model = new App.Backbone.Model.Page(App.Var.JSON);
        App.Var.View = new App.Backbone.View.Page({model: App.Var.Model,
                                                   loading: false,
                                                   loadError: false });
    },
    renderHomeError: function() {
        App.Var.View = new App.Backbone.View.Page({model: null,
                                                   loading: false,
                                                   loadError: true });
    },
    renderPageLoading: function() {
        App.Var.View = new App.Backbone.View.Page({model: null,
                                                   loading: true,
                                                   loadError: false});
    },

    showProfile: function() {
        console.log("Render Profile");
        $("#MasonryContainer").empty().masonry();
    },
};

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
    App.Var.Controller.showHome();
  },
  profile: function() {
    App.Var.Controller.showProfile();
  },
});
App.Var.Router = new App.Backbone.Router();

/******************************************************************************
 * Document ready
 */
$(document).ready(function() {
    $.ajaxSetup({ cache: false});

    App.Var.Controller.initialize();

    $("#NavHome").click(function(e) {
        e.preventDefault();
        console.log("HOME");
        App.Var.Router.navigate("/", {trigger: true});
    });
    $("#NavProfile").click(function(e) {
        e.preventDefault();
        console.log("PROFILE");
        App.Var.Router.navigate("/profile", {trigger: true});
    });
});

/* $eof */
