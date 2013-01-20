
App.Backbone.Model.Page = Backbone.Model.extend({
    defaults: {
        pageMode: App.Const.PageMode.EMPTY,
        lastPageMode: App.Const.PageMode.EMPTY,
        loggedInUserId: USER['id'],
        currentUserId: USER['id'],
        visionList: new App.Backbone.Model.VisionList(),
        selectedVisions: new App.Backbone.Model.VisionList(),
        
        /*  
            Page Option
            Added by Nikil
            1/9/2013 
        */
        option: App.Const.Options.None,
        otherVisions: new App.Backbone.Model.VisionList(),
        user: null,
        currentVision: null,
        activities: new App.Backbone.Model.ActivityList(),
    },
    initialize: function() {
    },
    // Getters
    pageMode: function() { return this.get("pageMode"); },
    pageString: function() { return App.Const.PageNames[this.pageMode()]; },
    loggedInUserId: function() { return this.get("loggedInUserId"); },
    currentUserId: function() { return this.get("currentUserId"); },
    visionList: function() { return this.get("visionList"); },
    selectedVisions: function() { return this.get("selectedVisions"); },
    /*  Added by Nikil
        1/9/2013 */
    option: function() { return this.get("option");},
    otherVisions: function() { return this.get("otherVisions"); },
    activities: function() { return this.get("activities"); },
    user: function() { return this.get("user"); },
    currentVision: function() { return this.get("currentVision"); },
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
    activeVisionList: function() {
        var pageMode = this.pageMode();
        if (pageMode == App.Const.PageMode.VISION_DETAILS) {
            pageMode = this.get("lastPageMode");
        }
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            pageMode == App.Const.PageMode.HOME_USER) {
            return this.otherVisions();
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            return this.selectedVisions();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (App.Var.Model.currentUserId() == USER.id) {
                return this.visionList();
            } else {
                return this.otherVisions();
            }
        } else {
            assert(false, "Invalid pageMode");
            return null;
        }
    },

    // Setters
    setPageMode: function(mode) {
        assert(mode > 0 && mode < App.Const.PageMode.INVALID,
               "Invalid page mode");
        // Always trigger view to change
        // This is there because we are using USER_PROFILE mode for
        // different users right now
        this.set({lastPageMode: this.pageMode()}, {silent: true});
        this.set({pageMode: mode}, {silent: true});
        this.trigger("change:pageMode");
    },
    clearLastPageMode: function() {
        this.set({lastPageMode: this.pageMode()}, {silent: true});
    },
    setUser: function(user) {
        this.set({ user : new App.Backbone.Model.User(user)}, {silent: true});
        this.trigger("change:user");
    },
    setCurrentVision: function(model) {
        return this.set({currentVision: model}, {silent : true});
    },
    setCurrentUserId: function(id) {
        var currentUserId = this.currentUserId();
        assert(id > 0, "Invalid user id");
        this.set({currentUserId: id}, {silent: true});
    },

    /*  Added by Nikil
        1/9/2013

        Page Option
        (passed in by second url parameter in Router.js)
        0 - nothing
        1 = show tour
    */
    setOption: function(option) {

        //Sanity Check
        if(option == App.Const.Options.NONE || option == App.Const.Options.ONBOARDING)
            this.set({ option: option}, {silent: true});

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
    setActivities: function(activities) {
        this.activities().reset(activities);
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
    addVisionComment: function(newComment) {
        // Find vision to add to
        if (DEBUG) console.log("NEW COMMENT: " + JSON.stringify(newComment));

        var vision = null;
        if (this.pageMode() == App.Const.PageMode.VISION_PAGE) {
            var vision = this.currentVision();
            vision.addComment(newComment);
        } else {
            var list = this.activeVisionList();
            for (var i = 0 ; i < list.length ; i++) {
                if (list.at(i).visionId() == newComment['visionId']) {
                    vision = list.at(i);
                }
            }
            if (null != vision) {
                vision.addComment(newComment);
            }
            // Trigger that height change and we need to re-layout
            this.trigger("new-comment");
        }
    },

    // THIS IS ONLY USED FOR MAKING SURE WE DON'T RE-RENDER FROM COMING BACK
    // AFTER VISION DETAILS RIGHT NOW
    cameFromVisionDetails: function() {
        return this.get("lastPageMode") == App.Const.PageMode.VISION_DETAILS;
    },
});

// $eof
