# Posts are a general feture that allows a user to post a comment.  Posts are associated with 
# comments.  Comments are comments on Posts.  It is a discussion board sort of relationship.
# In this site, Posts are associated with Feedback. Posts are posts on Feedback records and serve
# to start a conversation about the feedback record. 

# For a thorough description of this sort of code works, see the Feedback.py file which has
# thorough comments.

from app import app
from flask import render_template, redirect, url_for, request, session, flash
from app.classes.data import Post, Comment, Feedback, Video, User
from app.classes.forms import PostForm, CommentForm, UploadForm
from .users import admins
from requests_oauth2.services import GoogleClient
from requests_oauth2 import OAuth2BearerToken
import requests
import datetime as dt
from bson.objectid import ObjectId

@app.route('/explore')
def boxes():
 
    box = Video.objects()
    return render_template("interactive-resources.html", box=box)

# @app.route('/explore/<uploadId>')
# def post(uploadId):
  
#     upload = Explore.objects.get(pk=uploadId)
#     comments = Comment.objects(post=uploadId)
#     return render_template('commentform.html',post=post,comments=comments)

@app.route('/upload/<url>', methods=['GET', 'POST'])
def upload(url):

    form = UploadForm()
    form.url.data=url.replace('zzz','/')

    if form.validate_on_submit():

        newUpload = Video(
           
            subject=form.subject.data, 
            title =form.title.data,
            # tags = form.tags.data,
            body=form.body.data, 
            createdate=dt.datetime.now(),
            # contact_email = form.contact_email.data,
            url=form.url.data,

            vlink = form.vlink.data,
            # video = form.video.data,
            author=ObjectId(session['currUserId'])
        )
        newUpload.save()
        
        flash('Thank you for the upload!')
       
        newUpload.reload()

        return redirect('/explore')
   
    return render_template('submission.html', form=form)

# this final route will delete an existing feedback record
@app.route('/deletevideo/<videoID>')
def deletevideo(videoID):

    # retrieve the feedback object to be deleted
    deleteVideo = Video.objects.get(pk=videoID)
    # load the current user's object to check if they are allowed to delete the feedback record
    currUser = User.objects.get(gid=session['gid'])

    # check if the current user is the author of the feedback and it is still n new status or the current user is an admin
    if not (currUser.id == deleteVideo.author.id) and not currUser.email in admins:
        # if they do not have the right provleges send them back to the feedback
        flash(f'You cannot delete this job.')
        return redirect('/explore')

    # If they do have the privleges then do the delete thang and send the user to a list of all remaining feedback records
    deleteVideo.delete()
    return redirect('/explore') 
# @app.route('/newcomment/<postId>', methods=['GET', 'POST'])
# def newcomment(postId):
   
#     form=CommentForm()
#     post=Post.objects.get(pk=postId)
#     if form.validate_on_submit():
#         newComment = Comment(
#             comment=form.comment.data, 
#             createdate=datetime.datetime.now(), 
#             user=ObjectId(session['currUserId']),
#             post=post.id
#         )
#         newComment.save()
#         newComment.reload()
#         return redirect('/post/'+postId)
#     return render_template('commentform.html',post=post, form=form)

# @app.route('/deletecomment/<postId>/<commentId>')
# def deletecomment(postId, commentId):
 
#     deleteComment=Comment.objects.get(pk=commentId)
#     if str(deleteComment.user.id) == session['currUserId']:
#         deleteComment.delete()
#         flash('Comment deleted.')
#     else:
#         flash("You can't delete the comment because you don't own it.")
#     return redirect('/post/'+postId)

# @app.route('/upload', methods=['GET', 'POST'])
# def newpost(uploadID="none"):

#     form = PostForm()

#     if not jobid == "none":
#         postJob = Job.objects.get(pk=jobid)
#     else:
#         postJob = None
#     if not feedbackid == "none":
#         feedbackJob = Feedback.objects.get(pk=feedbackid)
#     else:
#         feedbackJob = None

#     if form.validate_on_submit():
#         newPost = Post(
#             subject=form.subject.data, 
#             body=form.body.data, 
#             createdate=datetime.datetime.now(), 
#             user=ObjectId(session['currUserId'])
#         )
#         newPost.save()
#         newPost.reload()

#         if not jobid == 'none':
#             newPost.update(job = ObjectId(jobid))
#         if not feedbackid == 'none':
#             newPost.update(feedback = ObjectId(feedbackid))

#         return render_template('post.html',post=newPost, job=postJob, feedback=feedbackJob)

#     flash('Fill out the form to create a new post')
#     return render_template('submission.html', form=form, job=postJob, feedback=feedbackJob)

# @app.route('/editpost/<postId>', methods=['GET', 'POST'])
# def editpost(postId):

#     editPost = Post.objects.get(pk=postId)
#     if str(editPost.user.id) == session['currUserId']:
#         form = PostForm()
#         if form.validate_on_submit():
#             editPost.update(
#                 subject=form.subject.data,
#                 body=form.body.data,
#                 modifydate=datetime.datetime.now()
#             )
#             editPost.reload()
#             flash('The post has been edited.')
#             return render_template('post.html', post=editPost)
#         flash('Change the fields below to edit your post')
#         form.subject.data = editPost.subject
#         form.body.data = editPost.body

#         return render_template('postform.html', form=form)
#     else:
#         flash("You can't edit this post because you are not the author.")
#         return redirect('/post/'+postId)

# @app.route('/deletepost/<postId>')
# def deletepost(postId):

#     deletePost = Post.objects.get(pk=postId)
#     if str(deletePost.user.id) == session['currUserId']:
#         deletePost.delete()
#         flash('Post was deleted')
#         posts=Post.objects()
#         return render_template('posts.html',posts=posts)
#     else:
#         flash("You can't delete this post because you are not the author")
#         return redirect('/post/'+postId)