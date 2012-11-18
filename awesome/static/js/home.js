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

/******************************************************************************
 * Utility functions for getting/setting global state
 */

function userLoggedIn() {
    return USER != null;
}

/******************************************************************************
 * AJAX functions
 */

function feedbackSaving() {
    $("#UserFeedbackSaved").hide();
    $("#UserFeedbackError").hide();
    $("#UserFeedbackSaving").show();
}
function feedbackSaved() {
    $("#UserFeedbackError").hide();
    $("#UserFeedbackSaving").hide();
    $("#UserFeedbackSaved").stop(true,true).show().fadeOut(5000);
}
function feedbackError() {
    $("#UserFeedbackSaving").hide();
    $("#UserFeedbackSaved").hide();
    $("#UserFeedbackError").show();
}

function doAjax(url, data, successFunc, errorFunc) {
    feedbackSaving();

    $.ajax({
        type: "POST",
        cache: false,
        contentType : "application/json",
        url: url,
        data: data,
        dataType: "json",
        beforeSend: function(jqXHR, settings) {
            if (jqXHR.overrideMimeType) {
                jqXHR.overrideMimeType("application/json");
            }
        },
        success: function(data, textStatus, jqXHR) {
            if (data.result == "success") {
                feedbackSaved();
                successFunc(data, textStatus, jqXHR);
            } else {
                feedbackError();
                errorFunc(jqXHR, textStatus, "JSON error");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            feedbackError();
            errorFunc(jqXHR, textStatus, errorThrown);
        },
        complete: function(jqXHR, textStatus) {},
    });
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
            TEST_VISION: 3,
            USER_PROFILE: 4,
            INVALID: 5, // Keep at end: we use to check validity of pageMode
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

/******************************************************************************
 * Backbone models
 */

App.Backbone.Model.User = Backbone.Model.extend({

});

App.Backbone.Model.Picture = Backbone.Model.extend({
    defaults: {
        id: -1,
        filename: "",
        url: "",
    },
    initialize: function() {
    },
    pictureId: function() { return this.get("id"); },
    url: function() { return this.get("url"); },
});

App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        id: -1,
        parentId: -1,
        userId: -1,
        text: "",
        picture: null,
        isSelected: false,
    },
    initialize: function() {
        this.set({
            picture: new App.Backbone.Model.Picture(this.get("picture"))
        });

        if (null != App.Var.Model &&
            null != App.Var.Model.getSelectedVision(this.visionId())) {
            this.set({isSelected: true});
        }
    },
    // Getters
    visionId: function() { return this.get("id"); },
    parentId: function() { return this.get("parentId"); },
    userId: function() { return this.get("userId"); },
    picture: function() { return this.get("picture"); },
    text: function() { return this.get("text"); },
    isSelected: function() { return this.get("isSelected"); },

    // Setters
    toggleSelected: function() {
        if (!this.isSelected()) {
            if (App.Var.Model.numSelectedVisions() <
                App.Const.MAX_SELECTED_VISIONS) {
                App.Var.Model.addToSelectedVisions(this);
            } else {
                return;
            }
        } else {
            App.Var.Model.removeFromSelectedVisions(this);
        }
        this.set({isSelected: !this.get("isSelected")});
    },
    deepClone: function() {
        var cloneModel = this.clone();
        cloneModel.set({ picture: this.picture().clone() });
        return cloneModel;
    },
});

App.Backbone.Model.VisionList = Backbone.Collection.extend({
    model: App.Backbone.Model.Vision
});

App.Backbone.Model.VisionComment = Backbone.Model.extend({

});

App.Backbone.Model.Page = Backbone.Model.extend({
    defaults: {
        pageMode: App.Const.PageMode.EMPTY,
        visionList: new App.Backbone.Model.VisionList(),
        selectedVisions: new App.Backbone.Model.VisionList(),
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
    selectedVisions: function() { return this.get("selectedVisions"); },
    getSelectedVision: function(visionId) {
        var list = this.selectedVisions().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
    },
    numSelectedVisions: function() {
        return this.selectedVisions().length;
    },

    // Setters
    setPageMode: function(mode) {
        assert(mode > 0 && mode < App.Const.PageMode.INVALID,
               "Invalid page mode");
        this.set({pageMode: mode});
    },
    setVisionList: function(visionList) {
        this.set({visionList: new App.Backbone.Model.VisionList(visionList) });
    },
    addToSelectedVisions: function(model) {
        var vision = this.getSelectedVision(model.visionId());
        if (vision == null) {
            // Note that we clone the model. We want our own copy for in
            // case we want to let the user edit it in some way
            this.selectedVisions().push(model.deepClone());
            return true;
        }
        return false;
    },
    removeFromSelectedVisions: function(model) {
        var vision = this.getSelectedVision(model.visionId());
        if (vision != null) {
            this.selectedVisions().remove(vision);
            return true;
        }
        return false;
    },
    moveSelectedVision: function(srcIndex, destIndex) {
        // We don't move silently here because we want to trigger
        // and update to the hidden input with the selected visions list
        var list = this.selectedVisions();
        var model = list.at(srcIndex);
        list.remove(model);
        list.add(model, {at: destIndex})
    },
    moveVision: function(srcIndex, destIndex) {
        // Move silently because the UI is already updated upon move
        var list = this.visionList();
        var model = list.at(srcIndex);
        list.remove(model, {silent: true});
        list.add(model, {at: destIndex, silent: true})
    },
});

/******************************************************************************
 * Backbone views
 */

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "li",
    className: "MasonryItem  MasonryBox",
    initialize: function() {
        _.bindAll(this, "itemSelect",
                        "mouseEnter", "mouseLeave");
        this.model.bind("change", this.render, this);
        this.render();
    },
    events: {
        "click .MasonryItemInner" : "itemSelect",
        "mouseenter .MasonryItemInner" : "mouseEnter",
        "mouseleave .MasonryItemInner" : "mouseLeave",
    },
    render: function() {
        var pageMode = App.Var.Model.pageMode();

        var selectedClass = "MasonryItemUnselected";
        if (pageMode == App.Const.PageMode.HOME_GUEST &&
            this.model.isSelected()) {
            selectedClass = "MasonryItemSelected";
        }
        var pictureDisplay = "none";
        var pictureUrl = "";
        if (null != this.model.picture()) {
            pictureDisplay = "block";
            pictureUrl = this.model.picture().url();
        }
        var cursorClass = "";
        var moveDisplay = "none";
        if (pageMode == App.Const.PageMode.TEST_VISION) {
            cursorClass = "MasonryItemMoveCursor";
        } else if (pageMode == App.Const.PageMode.HOME_GUEST) {
            cursorClass = "MasonryItemPointerCursor";
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            cursorClass = "MasonryItemPointerCursor";
            moveDisplay = "inline-block";
        }

        var variables = {text : this.model.text(),
                         selected: selectedClass,
                         pictureDisplay: pictureDisplay,
                         pictureUrl: pictureUrl,
                         cursorClass: cursorClass,
                         moveDisplay: moveDisplay,
                        };

        var template = _.template($("#VisionTemplate").html(), variables);
        $(this.el).html(template);

        return this;
    },
    itemSelect: function() {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.model.toggleSelected();
            this.mouseEnter();
        } else if (pageMode == App.Const.PageMode.HOME_USER ||
                   pageMode == App.Const.PageMode.TEST_VISION) {
            // Skip
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            $("#VisionDetailsModal").modal();
        } else {
            assert(false, "Invalid page mode in item select");
        }
    },
    mouseEnter: function() {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            if (!this.model.isSelected()) {
                $(this.el).find(".AddVisionOverlay").show();
            } else {
                $(this.el).find(".RemoveVisionOverlay").show();
            }
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            $(this.el).find(".VisionToolbar").show();
        }
    },
    mouseLeave: function() {
        var pageMode = App.Var.Model.pageMode();
        if (App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST) {
            $(this.el).find(".AddVisionOverlay").hide();
            $(this.el).find(".RemoveVisionOverlay").hide();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            $(this.el).find(".VisionToolbar").hide();
        }
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, // Changing page mode and rendering rest of page
                        "changePageMode",
                        "showPageLoading",
                        "hidePageLoading",
                        "showInfoBar",
                        "hideInfoBar",
                        // For onboarding
                        "showAddItemButton",
                        "hideAddItemButton",
                        "changeInSelectedVisions",
                        "selectedVisionsSortStart",
                        "selectedVisionsSortChange",
                        "selectedVisionsSortStop",
                        "renderSelectedVisions",
                        "renderSelectedVision",
                        // Show main page
                        "showHome",
                        "renderHome",
                        "renderHomeError",
                        // Rendering Main vision list
                        "renderVisionList",
                        "renderVision",
                        "sortStart",
                        "sortChange",
                        "sortStop",
                        "ajaxSortSuccess",
                        "ajaxSortError",
                        // Show user profile
                        "showProfile",
                        "renderProfile",
                        "renderProfileError");
        this.model.bind("change:pageMode", this.changePageMode, this);
        this.model.bind("change:visionList", this.renderVisionList, this);
        this.model.selectedVisions().bind("add", 
                                          this.changeInSelectedVisions,
                                          this);
        this.model.selectedVisions().bind("remove", 
                                          this.changeInSelectedVisions,
                                          this);
        // initialize a few variables
        this.selectedVisionMoveIndex = -1;
        this.moveIndex = -1;
    },

    /*
     * Changing page mode triggered by set of this.model.pageMode
     */
    changePageMode: function() {
        console.log("CHANGE MODE: " + this.model.pageMode());

        var pageMode = this.model.pageMode();

        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.showInfoBar(true);
            this.hideAddItemButton();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.TEST_VISION) {
            this.showInfoBar(false);
            this.hideAddItemButton();
            this.showTestVision();
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            this.hideInfoBar();
            this.hideAddItemButton();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            this.hideInfoBar();
            this.showAddItemButton();
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
            itemSelector: "li.MasonryItem",
            columnWidth:299
        }).imagesLoaded(function() {
            $("#MasonryContainer").masonry('reload');
        });
        if (App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE) {
            masonryContainer.sortable({
                items: "li.MasonryItem",
                handle: ".VisionToolbarMove",
                distance: 12,
                forcePlaceholderSize: true,
                tolerance: 'intersect',
                start: this.sortStart,
                change: this.sortChange,
                stop: this.sortStop,
            });
        }
    },
    renderVision: function(vision, index) {
        var vision = new App.Backbone.View.Vision({ model: vision });
        this.children.push(vision.el);
    },
    sortStart: function(event, ui) {
        console.log("Sort");
        ui.item.removeClass("MasonryItem");
        ui.item.parent().masonry('reload');

        this.moveIndex = ui.item.index();
    },
    sortStop: function(event, ui) {
        ui.item.addClass("MasonryItem");
        ui.item.parent().masonry('reload');
        var destIndex = ui.item.index();
        if (destIndex != this.moveIndex && this.moveIndex >= 0) {
            this.model.moveVision(this.moveIndex, destIndex);
        }
    },
    sortChange: function(event, ui) {
        ui.item.parent().masonry('reload');
    },
    ajaxSortSuccess: function(data, textStatus, jqXHR) {

    },
    ajaxSortError: function(jqXHR, textStatus, errorThrown) {

    },

    /*
     * Render test vision board
     */
    renderSelectedVisions: function() {
        var masonryContainer = $("#TestVisionContainer").first();

        masonryContainer.empty();
        this.testVisions = []

        this.model.selectedVisions().each(this.renderSelectedVision);

        masonryContainer.append(this.testVisions);

        // TODO: Don't need to reload once we know heights of images
        masonryContainer.masonry({
            itemSelector: "li.MasonryItem",
            columnWidth:299
        }).imagesLoaded(function() {
            $("#TestVisionContainer").masonry('reload');
        });
        masonryContainer.sortable({
            items: "li.MasonryItem",
            distance: 12,
            forcePlaceholderSize: true,
            tolerance: 'intersect',
            start: this.selectedVisionsSortStart,
            change: this.selectedVisionsSortChange,
            stop: this.selectedVisionsSortStop,
        });
    },
    renderSelectedVision: function(vision, index) {
        var vision = new App.Backbone.View.Vision({ model: vision });
        this.testVisions.push(vision.el);
    },
    selectedVisionsSortStart: function(event, ui) {
        ui.item.removeClass("MasonryItem");
        ui.item.parent().masonry('reload');

        this.selectedVisionMoveIndex = ui.item.index();
    },
    selectedVisionsSortStop: function(event, ui) {
        ui.item.addClass("MasonryItem");
        ui.item.parent().masonry('reload');
        var destIndex = ui.item.index();
        if (destIndex != this.selectedVisionMoveIndex &&
            this.selectedVisionMoveIndex >= 0) {
            this.model.moveSelectedVision(this.selectedVisionMoveIndex,
                                          destIndex);
            console.log("SORT: " +
                        JSON.stringify(this.model.selectedVisions()));
        }
    },
    selectedVisionsSortChange: function(event, ui) {
        ui.item.parent().masonry('reload');
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
     * Show/hide Add Item button
     */
    showAddItemButton: function() { $("#AddItemButton").show(); },
    hideAddItemButton: function() { $("#AddItemButton").hide(); },

    /*
     * Show/hide information bar
     *
     * Input for now: true = info, false = test vision
     * *** TODO: make this better ***
     */
    showInfoBar: function(showInfo) {
        if (showInfo) {
            $("#TestVisionInfoContainer").hide();
            $("#InfoContainer").show();
        } else {
            $("#InfoContainer").hide();
            $("#TestVisionInfoContainer").show();
        }
        $("#InfoContainerPadding").show();
    },
    hideInfoBar: function() {
        $("#InfoContainer").hide();
        $("#InfoContainerPadding").hide();
    },

    changeInSelectedVisions: function() {
        console.log("CHANGE");
        var length = this.model.numSelectedVisions();
        if (length <= 0) {
            $("#SelectedVisionCountContainer").hide();

            $("#ViewBoardButton").hide();
            $("#RegisterButton").show();
        } else {
            $("#SelectedVisionCountContainer").show();
            $("#SelectedVisionCount").html(length);

            $("#RegisterButton").hide();
            $("#ViewBoardButton").show();
        }
        console.log("Visions: " + JSON.stringify(this.model.selectedVisions()));

        // Update hidden field in registration
        var visionIds = [];
        for (var i = 0 ; i < length ; i++) {
            visionIds.push(this.model.selectedVisions().at(i).visionId());
        }
        $("#UserSelectedVisions").first().attr("value", JSON.stringify(visionIds));
        console.log("VISION LIST: " + JSON.stringify(visionIds));
    },

    /*
     * Render home page
     */
    showHome: function() {
        this.showPageLoading();
        $("#TestVisionContainer").empty().hide();
        $("#MasonryContainer").show();

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
     * Show test vision
     */
    showTestVision: function() {
        $("#MasonryContainer").hide();
        $("#TestVisionContainer").empty().show();
        this.renderSelectedVisions();
    },

    /*
     * Render user profile page
     */
    showProfile: function() {
        this.showPageLoading();
        $("#TestVisionContainer").empty().hide();
        $("#MasonryContainer").show();

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
    "view_board"      : "viewBoard",
    "*action"         : "home",
  },
  home: function() {
    if (userLoggedIn()) {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_USER);
    } else {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_GUEST);
    }
  },
  viewBoard: function() {
      if (!userLoggedIn() &&
          App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST) {
        App.Var.Model.setPageMode(App.Const.PageMode.TEST_VISION);
      } else {
        assert(false, "Shouldn't be logged in or come from another page");
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
    $("#BackToMainPageButton").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/", {trigger: true});
    });
    $("#NavProfile").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/profile", {trigger: true});
    });

    $("#ViewBoardButton").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/view_board", {trigger: true});
    });

    $("#ReloadHome").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showHome();
    });
    $("#ReloadProfile").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showProfile();
    });
    $("#JoinSiteButton").click(function() {
        $("#RegisterForm").first().submit();
    });

    $("#AddItemButton").click(function() {
        $("#AddItemModal").modal();
    });
});

/* $eof */
