from flask import Flask, request, render_template, redirect, flash, session

from surveys import satisfaction_survey

from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "oh-so-secret"

debug = DebugToolbarExtension(app)

@app.route('/')
def show_survey_start():
    """Root page should show the user
         - title of the survey
         - the instructions
         - button to start the survey
    """

    return render_template('form_start.html.j2', survey=satisfaction_survey)

@app.route("/start", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    session["responses"] = []

    return redirect("/questions/0")

@app.route("/questions/<int:qidx>")
def present_question(qidx):
    """Show them the question they are on"""

    responses = session.get("responses")
    
    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) != qidx):
        flash(f"Invalid question id: {qidx}.")
        return redirect(f"/questions/{len(responses)}")

    if (responses == None):
        return redirect("/")

    question = satisfaction_survey.questions[qidx]
    return render_template("question.html.j2", survey=satisfaction_survey, question=question)
    
@app.route("/answer", methods=["POST"])
def handle_answer():
    """Save the answer and move to next question"""

    # get responses
    responses = session["responses"]

    # punish them for not answering the question
    if (request.form.get('answer') is None):
        return redirect(f"/question/{len(responses)}")
        
    # Get the answer from the html page
    choice = request.form['answer']

    # append choice to responses
    responses.append(choice)
    session["responses"] = responses

    # Show them the end of the survey or move to next question if not complete
    if (len(responses) == len(satisfaction_survey.questions)):
        return redirect("/finished")
    


    else:
        return redirect(f"/questions/{len(responses)}")

@app.route("/finished")
def display_complete():
    return render_template("complete.html.j2", 
                            survey=satisfaction_survey,
                            qa=zip(satisfaction_survey.questions, 
                                   session["responses"]))