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

// TODO: BE SAFER EVERYONE FOR IF USER IS LOGGED IN (back end should be OK tho)
function userLoggedIn() {
    return USER.id > 0;
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
                console.log("ERROR: " + JSON.stringify(data));
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
            GUEST_PROFILE: 5,
            INVALID: 6, // Keep at end: we use to check validity of pageMode
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
        largeUrl: "",
        mediumUrl: "",
        smallUrl: "",
    },
    initialize: function() {
    },
    pictureId: function() { return this.get("id"); },
    largeUrl: function() { return this.get("largeUrl"); },
    mediumUrl: function() { return this.get("mediumUrl"); },
    smallUrl: function() { return this.get("smallUrl"); },
});

App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
    },
    initialize: function() {
    },
    visionCommentId: function() { return this.get("id"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
});
App.Backbone.Model.VisionCommentList = Backbone.Collection.extend({
    model: App.Backbone.Model.VisionComment
});

App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        id: -1,
        parentId: -1,
        rootId: -1,
        userId: -1,
        text: "",
        name: "",
        picture: null,
        comments: null,
        isSelected: false,
    },
    initialize: function() {
        this.set({
            picture: new App.Backbone.Model.Picture(this.get("picture")),
            comments: new App.Backbone.Model.VisionCommentList(this.get("comments")),
        });

        if (null != App.Var.Model &&
            null != App.Var.Model.getSelectedVision(this.visionId())) {
            this.set({isSelected: true});
        }
    },
    // Getters
    visionId: function() { return this.get("id"); },
    parentId: function() { return this.get("parentId"); },
    rootId: function() { return this.get("rootId"); },
    userId: function() { return this.get("userId"); },
    picture: function() { return this.get("picture"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    isSelected: function() { return this.get("isSelected"); },
    comments: function() { return this.get("comments"); },

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

App.Backbone.Model.Page = Backbone.Model.extend({
    defaults: {
        pageMode: App.Const.PageMode.EMPTY,
        loggedInUserId: USER['id'],
        currentUserId: USER['id'],
        visionList: new App.Backbone.Model.VisionList(),
        selectedVisions: new App.Backbone.Model.VisionList(),
        otherVisions: new App.Backbone.Model.VisionList(),
    },
    initialize: function() {
    },
    // Getters
    pageMode: function() { return this.get("pageMode"); },
    loggedInUserId: function() { return this.get("loggedInUserId"); },
    currentUserId: function() { return this.get("currentUserId"); },
    visionList: function() { return this.get("visionList"); },
    selectedVisions: function() { return this.get("selectedVisions"); },
    otherVisions: function() { return this.get("otherVisions"); },
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
        // Always trigger view to change
        // This is there because we are using USER_PROFILE mode for
        // different users right now
        this.set({pageMode: mode}, {silent: true});
        this.trigger("change:pageMode");
    },
    setCurrentUserId: function(id) {
        var currentUserId = this.currentUserId();
        assert(id > 0, "Invalid user id");
        this.set({currentUserId: id}, {silent: true});
    },
    setVisionList: function(visionList) {
        // Note: need to use reset so that the methods bound to this collection
        //       still get called
        this.visionList().reset(visionList);
    },
    setOtherVisions: function(visionList) {
        // Note: need to use reset so that the methods bound to this collection
        //       still get called
        this.otherVisions().reset(visionList);
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
    inVisionList: function(visionModel) {
        var list = this.visionList().where({id: visionModel.visionId()});
        var rootList = this.visionList().where({rootId: visionModel.rootId()});
        return (list.length > 0) || (rootList.length > 0);
    },
    getVisionInList: function(visionId) {
        var list = this.visionList().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
    },
    getInOtherVisions: function(visionId) {
        var list = this.otherVisions().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
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
    deleteVision: function(visionId) {
        var toRemove = this.getVisionInList(visionId);
        assert(toRemove != null, "Couldn't find vision id to remove");
        this.visionList().remove(toRemove);
    },
    repostVisionDone: function(repostId, newVision) {
        // Add new vision to visionList
        this.visionList().unshift(new App.Backbone.Model.Vision(newVision),
                                  {silent: true});
        // Trigger change in repostId so we re-render it as in the vision list
        var repostModel = this.getInOtherVisions(repostId);
        if (null != repostModel) {
            repostModel.trigger("change");
        }
    },
    addVision: function(newVision) {
        // Add new vision to visionList
        this.visionList().unshift(new App.Backbone.Model.Vision(newVision));
    },
});

/******************************************************************************
 * Backbone views
 */

App.Backbone.View.VisionComment = Backbone.View.extend({
    className: "VisionComment",
    initialize: function() {
        //_.bindAll(this, "");
        this.render();
    },
    render: function() {
        var variables = { 'text': this.model.text() }
        var template = _.template($("#VisionCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
});

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "li",
    className: "MasonryItem  MasonryBox",
    initialize: function() {
        _.bindAll(this, "itemSelect", "renderComment",
                        "mouseEnter", "mouseLeave",
                        "repostVision", "removeVision", "gotoUser");
        this.model.bind("change", this.render, this);

        this.render();
    },
    events: {
        "click .MasonryItemInner" : "itemSelect",
        "mouseenter .MasonryItemInner" : "mouseEnter",
        "mouseleave .MasonryItemInner" : "mouseLeave",
        "click .VisionToolbarRepost"   : "repostVision",
        "click .VisionToolbarRemove"   : "removeVision",
        "click .VisionUserName"        : "gotoUser",
    },
    render: function() {
        var pageMode = App.Var.Model.pageMode();

        var selectedClass = "MasonryItemUnselected";
        var removeOverlayDisplay = "none";
        if ((pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) &&
            this.model.isSelected()) {
            selectedClass = "MasonryItemSelected";
            removeOverlayDisplay = "block";
        }
        var pictureDisplay = "none";
        var pictureUrl = "";
        if (null != this.model.picture()) {
            pictureDisplay = "block";
            pictureUrl = this.model.picture().mediumUrl();
        }
        var cursorClass = "";
        var moveDisplay = "none";
        var removeDisplay = "none";
        var repostDisplay = "none";
        var mineDisplay = "none";
        var nameDisplay = "none";
        if (pageMode == App.Const.PageMode.TEST_VISION) {
            cursorClass = "MasonryItemMoveCursor";
            removeDisplay = "inline-block";
        } else if (pageMode == App.Const.PageMode.HOME_GUEST) {
            cursorClass = "MasonryItemPointerCursor";
            nameDisplay = "block";
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            nameDisplay = "block";
            if (App.Var.Model.inVisionList(this.model)) {
                mineDisplay = "inline-block";
                selectedClass = "MasonryItemSelected";
            } else {
                repostDisplay = "inline-block";
            }
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (userLoggedIn()) {
                if (App.Var.Model.currentUserId() == USER.id) {
                    moveDisplay = "inline-block";
                } else {
                    if (App.Var.Model.inVisionList(this.model)) {
                        mineDisplay = "inline-block";
                        selectedClass = "MasonryItemSelected";
                    } else {
                        repostDisplay = "inline-block";
                    }
                }
            }
            cursorClass = "MasonryItemPointerCursor";
        }

        var variables = {text : this.model.text(),
                         selected: selectedClass,
                         pictureDisplay: pictureDisplay,
                         pictureUrl: pictureUrl,
                         cursorClass: cursorClass,
                         moveDisplay: moveDisplay,
                         removeDisplay: removeDisplay,
                         repostDisplay: repostDisplay,
                         mineDisplay: mineDisplay,
                         removeOverlayDisplay: removeOverlayDisplay,
                         name: this.model.name(),
                         nameDisplay: nameDisplay,
                         userId: this.model.userId(),
                        };

        var template = _.template($("#VisionTemplate").html(), variables);
        $(this.el).html(template);

        this.comments = []
        this.model.comments().each(this.renderComment);
        $(this.el).find(".VisionCommentContainer").append(this.comments);

        return this;
    },
    renderComment: function(comment, index) {
        var comment = new App.Backbone.View.VisionComment({ model: comment });
        this.comments.push(comment.el);
    },
    itemSelect: function(e) {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) {
            this.model.toggleSelected();
            this.mouseEnter();
        } else if (pageMode == App.Const.PageMode.HOME_USER ||
                   pageMode == App.Const.PageMode.TEST_VISION) {
            // Skip
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            App.Var.View.showVisionDetails(this.model);
        } else {
            assert(false, "Invalid page mode in item select");
        }
    },
    mouseEnter: function() {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) {
            if (!this.model.isSelected()) {
                $(this.el).find(".AddVisionOverlay").show();
            }
        } else if (pageMode == App.Const.PageMode.TEST_VISION ||
                   pageMode == App.Const.PageMode.HOME_USER ||
                   pageMode == App.Const.PageMode.USER_PROFILE) {
            $(this.el).find(".VisionToolbarConditional").show();
        }
    },
    mouseLeave: function() {
        var pageMode = App.Var.Model.pageMode();
        if (App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) {
            $(this.el).find(".AddVisionOverlay").hide();
        } else if (pageMode == App.Const.PageMode.TEST_VISION ||
                   pageMode == App.Const.PageMode.HOME_USER ||
                   pageMode == App.Const.PageMode.USER_PROFILE) {
            $(this.el).find(".VisionToolbarConditional").hide();
        }
    },
    repostVision: function(e) {
        e.preventDefault();
        App.Var.View.repostVision(this.model);
    },
    removeVision: function(e) {
        e.preventDefault();
        if (App.Var.Model.pageMode() == App.Const.PageMode.TEST_VISION) {
            App.Var.Model.removeFromSelectedVisions(this.model);
        } else {
            assert(false, "Should be in test vision page");
        }
    },
    gotoUser: function(e) {
        e.stopPropagation();    // prevent propagating to other handlers
        e.preventDefault();     // prevent following link
        App.Var.Router.navigate("/user/" + this.model.userId(),
                                {trigger: true});
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "activeVisionList",
                        "showVisionDetails",
                        "deleteVision",
                        "ajaxDeleteVisionSuccess",
                        "ajaxDeleteVisionError",
                        "repostVision",
                        "ajaxRepostVisionSuccess",
                        "ajaxRepostVisionError",
                        // Changing page mode and rendering rest of page
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
        this.model.otherVisions().bind("reset", 
                                       this.renderVisionList,
                                       this);
        this.model.visionList().bind("add", 
                                     this.renderVisionList,
                                     this);
        this.model.visionList().bind("remove", 
                                     this.renderVisionList,
                                     this);
        this.model.visionList().bind("reset", 
                                     this.renderVisionList,
                                     this);
        this.model.selectedVisions().bind("add", 
                                          this.changeInSelectedVisions,
                                          this);
        this.model.selectedVisions().bind("remove", 
                                          this.changeInSelectedVisions,
                                          this);
        // initialize a few variables
        this.selectedVisionMoveIndex = -1;
        this.srcIndex = -1;
        this.currentVision = null;
    },
    repostVision: function(visionModel) {
        assert(visionModel != null, "Vision model to repost is null");
        if (visionModel != null) {
            console.log("REPOST: " + visionModel.visionId());
            doAjax("/api/user/" + USER['id'] + "/repost_vision",
                   JSON.stringify({
                                    'visionId' : visionModel.visionId(),
                                  }),
                   this.ajaxRepostVisionSuccess,
                   this.ajaxRepostVisionError
            );
        }
    },
    ajaxRepostVisionSuccess: function(data, textStatus, jqXHR) {
        this.model.repostVisionDone(data.repostParentId, data.newVision);
    },
    ajaxRepostVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    showVisionDetails: function(visionModel) {
        this.currentVision = visionModel;

        // Note: jQuery text() method escapes html brackets and stuff
        $("#CurrentVisionText").text(this.currentVision.text());

        $("#VisionDetailsModal").modal();
    },
    deleteVision: function() {
        if (this.currentVision != null) {
            console.log("DELETE");
            doAjax("/api/user/" + USER['id'] + "/delete_vision",
                   JSON.stringify({
                                    'visionId' : this.currentVision.visionId(),
                                  }),
                   this.ajaxDeleteVisionSuccess,
                   this.ajaxDeleteVisionError
            );
        }
    },
    ajaxDeleteVisionSuccess: function(data, textStatus, jqXHR) {
        console.log("REMOVED ID: " + data.removedId);
        this.model.deleteVision(data.removedId);
        $("#VisionDetailsModal").modal("hide");
    },
    ajaxDeleteVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
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
            if (userLoggedIn()) {
                this.hideInfoBar();
                this.showAddItemButton();
            } else {
                this.showInfoBar(true);
                this.hideAddItemButton();
            }
            this.showProfile();
        } else {
            assert(false, "Invalid page mode in changePageMode");
        }
    },

    activeVisionList: function() {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            pageMode == App.Const.PageMode.HOME_USER) {
            return this.model.otherVisions();
        } else if (pageMode == App.Const.PageMode.TEST_VISION) {
            return this.model.selectedVisions();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (App.Var.Model.currentUserId() == USER.id) {
                return this.model.visionList();
            } else {
                return this.model.otherVisions();
            }
        } else {
            assert(false, "Invalid pageMode");
            return null;
        }
    },

    /*
     * Render vision list: triggered by set of this.model.visionList
     */
    renderVisionList: function() {
        console.log("RENDER VISION LIST");
        var masonryContainer = $("#MasonryContainer").first();

        masonryContainer.empty();
        this.children = []

        this.activeVisionList().each(this.renderVision);

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

        this.srcIndex = ui.item.index();
    },
    sortStop: function(event, ui) {
        ui.item.addClass("MasonryItem");
        ui.item.parent().masonry('reload');
        this.destIndex = ui.item.index();
        if (this.destIndex != this.srcIndex && this.srcIndex >= 0) {
            var visionId = this.model.visionList().at(this.srcIndex).visionId();
            doAjax("/api/user/" + USER['id'] + "/move_vision",
                   JSON.stringify({'visionId' : visionId,
                                   'srcIndex' : this.srcIndex,
                                   'destIndex' : this.destIndex}),
                   this.ajaxSortSuccess,
                   this.ajaxSortError
            );
        }
    },
    sortChange: function(event, ui) {
        ui.item.parent().masonry('reload');
    },
    ajaxSortSuccess: function(data, textStatus, jqXHR) {
        this.model.moveVision(this.srcIndex, this.destIndex);
    },
    ajaxSortError: function(jqXHR, textStatus, errorThrown) {
        this.renderVisionList();
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

        // Update hidden field in registration
        var visionIds = [];
        for (var i = 0 ; i < length ; i++) {
            visionIds.push(this.model.selectedVisions().at(i).visionId());
        }
        $("#UserSelectedVisions").first().attr("value", JSON.stringify(visionIds));
        console.log("VISION LIST: " + JSON.stringify(visionIds));

        // If we are in test vision mode, we need to re-render vision
        if (App.Var.Model.pageMode() == App.Const.PageMode.TEST_VISION) {
            this.renderSelectedVisions();
        }
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
        if (this.model.visionList().isEmpty()) {
            // TODO: be smarter about when to load and set visionList later
            //       do this first so rendering of other visions has proper
            //       vision list to process
            this.model.setVisionList(App.Var.JSON.visionList);
        }
        this.model.setOtherVisions(App.Var.JSON.otherVisions);
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

        var ajaxUrl = "/api/user/" + App.Var.Model.currentUserId() + "/visions";

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
        if (App.Var.Model.currentUserId() != USER.id) {
            this.model.setOtherVisions(App.Var.JSON.otherVisions);
        }
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
    "user/:userId"    : "profile",
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
          (App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST ||
           App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE)) {
        App.Var.Model.setPageMode(App.Const.PageMode.TEST_VISION);
      } else {
        assert(false, "Shouldn't be logged in or come from another page");
      }
  },
  profile: function(userId) {
    App.Var.Model.setCurrentUserId(userId);
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
        App.Var.Router.navigate("/user/" + USER['id'], {trigger: true});
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

    $("#VisionDeleteButton").click(function() {
        App.Var.View.deleteVision();
    });

    /*
     * File upload stuff
     */
    function toggleAddVisionSubmit() {
        var enable = false;
        var fileName = $("#FileUploadInput").val();
        if (fileName != "") {
            enable = true;
        }
        /* Should we allow text w/o image?
        var text = $.trim($("#InputText").val());
        if (text != "") {
            console.log("TEXT: " + text);
            enable = true;
        }
        */
        if (enable == true) {
            $("#AddVisionSubmit").removeAttr("disabled");
        } else {
            $("#AddVisionSubmit").attr("disabled", "disabled");
        }
    }

    $("#AddItemButton").click(function() {
        $("#AddVisionModal").modal();
        $("#FileUploadInput").val("");
        $("#FileUploadInput").removeAttr("disabled");
        $("#FileUploadNoPreview").show();
        $("#FileUploadLoading").hide();
        $("#FileUploadInvalid").hide();
        $("#FileUploadImageContainer").hide();
        $("#InputText").val("");
        $("#AddVisionSubmit").attr("disabled", "disabled");
    });
    $("#FileUploadInput").change(function() {
        var fileName = $("#FileUploadInput").val();
        if (fileName != "") {
            // Show user we are processing file
            console.log("UPLOAD: " + fileName);

            // Submit!
            $("#FileUploadForm").submit();

            // disable file upload while we are uploading this file
            $("#FileUploadInput").attr("disabled", "disabled");
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").show();
            $("#FileUploadInvalid").hide();
            $("#FileUploadImageContainer").hide();
        }
    });
    $("#FileUploadTarget").load(function() {
        // Re-enable the file upload input
        $("#FileUploadInput").removeAttr("disabled");

        console.log("File uploaded!");
        var jsonText = $("#FileUploadTarget").contents().find("body").html();
        var result  = eval('(' + jsonText+ ')');
        if (result && result.result == "success") {
            // Show image uploaded
            console.log("url: " + result.url);
            // Append unique string to end of url to smash image caching
            var t  = new Date().getTime();
            var url = $.trim(result.url) + "?" + t.toString();

            $("#FileUploadNoPreview").hide();
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").hide();
            $("#FileUploadImage").attr("src", url);
            $("#FileUploadImageContainer").show();
        } else {
            // Clear the file upload image feedback
            console.log("UPLOAD ERROR");
            $("#FileUploadInvalid").show();
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").hide();
            $("#FileUploadImageContainer").hide();
            $("#FileUploadInput").val("");
        }
        toggleAddVisionSubmit();
    });
    /*
    $("#InputText").keyup(toggleAddVisionSubmit);
    $("#InputText").bind('paste',toggleAddVisionSubmit);
    $("#InputText").bind('cut',toggleAddVisionSubmit);
    */
    $("#AddVisionSubmit").click(function() {
        var useImage = false;
        if ($("#FileUploadInput").val() != "") {
            useImage = true;
        }

        var text = $.trim($("#InputText").val());

        doAjax("/api/user/" + USER['id'] + "/add_vision",
                JSON.stringify({'useImage' : useImage,
                                'text' : text}),
                // success
                function(data, textStatus, jqXHR) {
                    console.log("Success: " + JSON.stringify(data));
                    App.Var.Model.addVision(data.newVision);
                    $("#AddVisionModal").modal("hide");
                },
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    });
});

/* $eof */
