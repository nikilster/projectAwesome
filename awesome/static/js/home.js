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
App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        visionId: -1,
        category: "",
        text: "",
        photoUrl: "",
        isPrivate: false,
        isGloballyShared: false,
        isFbShared: false,
    },
    initialize: function() {
        /*
        this.set({
            visionId: this.get("visionId"),
            category: this.get("category"),
            text: this.get("text"),
            photoUrl: this.get("photoUrl"),
            isPrivate: this.get("isPrivate"),
            isGloballyShared: this.get("isGloballyShared"),
            isFbShared: this.get("isFbShared"),
        });
        */
    },
    visionId: function() { return this.get("visionId"); },
    category: function() { return this.get("category"); },
    text: function() { return this.get("text"); },
    photoUrl: function() { return this.get("photoUrl"); },
    isPrivate: function() { return this.get("isPrivate"); },
    isGloballyShared: function() { return this.get("isGloballyShared"); },
    isFbShared: function() { return this.get("isFbShared"); },
});

App.Backbone.Model.VisionList = Backbone.Collection.extend({
    model: App.Backbone.Model.Vision
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
        this.render();
    },
    render: function() {
        var variables = {text : this.model.text() };

        if (this.model.photoUrl() == "") {
            var template = _.template($("#VisionTemplate").html(), variables);
            $(this.el).html(template);
        } else {
            var template = _.template($("#VisionImageTemplate").html(), variables);
            $(this.el).html(template);
        }

        return this;
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "renderVisionList", "renderVision");
        this.render();
    },
    render: function() {
        if (this.options.loading == false && this.options.loadError == false) {
            this.renderVisionList();
        }
    },
    renderVisionList: function() {
        var masonryContainer = $("#MasonryContainer").first();

        masonryContainer.empty();
        this.children = []

        this.model.visionList().each(this.renderVision);

        masonryContainer.append(this.children);

        masonryContainer.masonry({
            itemSelector: "div.MasonryItem",
            columnWidth:299
        });
    },
    renderVision: function(vision, index) {
        console.log("VISON: " + JSON.stringify(vision));
        var vision = new App.Backbone.View.Vision({ model: vision });
        this.children.push(vision.el);
    },
});

/******************************************************************************
 * Controller
 */

App.Var.Controller = {
    initialize: function() {
        App.Var.Controller.showVisionBoard();
    },
    showVisionBoard: function() {
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
                App.Var.Controller.renderVisionBoardError();
            },
            success: function(data, textStatus, jqXHR) {
                //console.log("DATA: " + JSON.stringify(data));
                App.Var.JSON = data;
                App.Var.Controller.renderVisionBoard();
            }
        });
    },
    renderVisionBoard: function() {
        App.Var.Model = new App.Backbone.Model.Page(App.Var.JSON);
        App.Var.View = new App.Backbone.View.Page({model: App.Var.Model,
                                                   loading: false,
                                                   loadError: false });
    },
    renderVisionBoardError: function() {
        App.Var.View = new App.Backbone.View.Page({model: null,
                                                   loading: false,
                                                   loadError: true });
    },
    renderPageLoading: function() {
        App.Var.View = new App.Backbone.View.Page({model: null,
                                                   loading: true,
                                                   loadError: false});
    },
};

/******************************************************************************
 * Document ready
 */
$(document).ready(function() {
    $.ajaxSetup({ cache: false});

    App.Var.Controller.initialize();
});

/* $eof */
