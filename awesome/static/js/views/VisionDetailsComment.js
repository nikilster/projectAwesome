App.Backbone.View.VisionDetailsComment = Backbone.View.extend({
    className: "VisionDetailsComment",
    sel: {
        LIKE: ".VisionLikeInfo",
    },
    initialize: function() {
        _.bindAll(this, "showLikes");
        this.urlTarget = this.options.urlTarget;
        this.render();
    },
    render: function() {
        var pictureVisibility = "Hidden";
        var picture = "";
        var height = 0;
        if (this.model.hasPicture()) {
            picture = this.model.picture().largeUrl();
            pictureVisibility = "";
            height = this.model.picture().largeHeightWithWidth(360);
        }

        var variables = { 'authorId' : this.model.authorId(),
                          'text': linkify(this.model.text()),
                          'name': this.model.author().fullName(),
                          'userPicture': this.model.author().picture(),
                          'pictureVisibility': pictureVisibility,
                          'picture' : picture,
                          'height' : height,
                          'urlTarget': this.urlTarget,
                          'created' : this.model.timeString(), }
        var template = _.template($("#VisionDetailsCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        if (this.model.like() != null) {
            var likeView = new App.Backbone.View.Like(
                                                { model: this.model.like(),
                                                  parentView: this });
            $(this.el).find(this.sel.LIKE).append(likeView.el);
        }

        return this;
    },
    showLikes: function(e) {
        App.Var.View.showVisionCommentLikes(this.model.visionCommentId());
    },
});

