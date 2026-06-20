from django.urls import path

from . import views

urlpatterns = [path("", views.index, name="index"),
               path("AddElectionDate.html", views.AddElectionDate, name="AddElectionDate"),
	       path("AddElectionDateAction", views.AddElectionDateAction, name="AddElectionDateAction"),
	       path("AddVoter.html", views.AddVoter, name="AddVoter"),
	       path("AddVoterAction", views.AddVoterAction, name="AddVoterAction"),
	       path("AddCandidate.html", views.AddCandidate, name="AddCandidate"),
	       path("AddCandidateAction", views.AddCandidateAction, name="AddCandidateAction"),
	       path("AdminLogin", views.AdminLogin, name="AdminLogin"),
	       path("Admin.html", views.Admin, name="Admin"),
	       path("Vote.html", views.Vote, name="Vote"),
	       path("ViewCount", views.ViewCount, name="ViewCount"),	
	       path("FinishVote", views.FinishVote, name="FinishVote"),
	       path("UserLogin", views.UserLogin, name="UserLogin"),
	       path("User.html", views.User, name="User"),
	       path("Graph", views.Graph, name="Graph"),
	       path("ViewUserResult", views.ViewUserResult, name="ViewUserResult"),	       
]