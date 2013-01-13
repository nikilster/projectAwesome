/* Like.js : Like View
 *
 * parentView: need to provide a parent view for this like. The parentView
 *             MUST include a model that has the toggleLike() method
 *             implemented.
 */
App.Backbone.View.Like = Backbone.View.extend({
    tagName: "span",
    sel: {
        LIKE_BUTTON: ".VisionLike",
    },
    initialize: function() {
        _.bindAll(this, "likeClick");

        assert(this.options.parentView != null, "No parent for like view");
        this.parentView = this.options.parentView;

        this.model.bind("change", this.render, this);

        this.render();
    },
    events: function() {
        var _events = {};

        _events["click " + this.sel.LIKE_BUTTON] = "likeClick";

        return _events;
    },
    render: function() {
        var likeCount = this.model.likeCount();
        var likeText = "";
        var likeVisibility = "Hidden";
        var thumbVisibility = "Hidden";
        if (userLoggedIn() && this.model.userLike() != null) {
            if (this.model.userLike() == true) {
                likeText = "Unlike";

                thumbVisibility = "";
                likeCount = likeCount - 1;
                if (likeCount > 0) {
                    likeCount = "You + " + likeCount;
                } else {
                    likeCount = "You";
                }
            } else {
                likeText = "Like";
                if (likeCount > 0) {
                    thumbVisibility = "";
                } else {
                    likeCount = "";
                }
            }
            likeVisibility = "";
        } else {
            if (likeCount > 0) {
                thumbVisibility = "";
            } else {
                likeCount = "";
            }
        }

        var variables = {likeCount: likeCount,
                         likeText: likeText,
                         likeVisibility: likeVisibility,
                         thumbVisibility: thumbVisibility,
                        };
        var template = _.template($("#VisionLikeTemplate").html(), variables);
        $(this.el).html(template);

        return this;
    },
    likeClick: function() {
        this.parentView.model.toggleLike();
    },
});

// $eof
