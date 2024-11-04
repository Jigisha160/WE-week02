import random
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
import os
# Create your views here.
# def index(request: HttpRequest) -> HttpResponse: 
#     return HttpResponse("Hello, world. This is my first Django app.")
def load_words():
    # Load English words from file
    file_path = os.path.join(os.path.dirname(__file__), 'words.txt')
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

def get_random_word() -> str:
    words = load_words()
    return random.choice(words).upper()

def index(request: HttpRequest):
    # Initialize or retrieve session variables
    if 'wordle_word' not in request.session:
        request.session['wordle_word'] = get_random_word()
        request.session['attempts'] = 6

    if request.method == 'POST':
        # User's guess from the form
        guess = request.POST.get('guess', '').upper()

        # Handle new game setup
        if 'reset' in request.POST:
            request.session.flush()  # Clear session for new game
            return JsonResponse({'message': 'New game started!'})

        # Ensure a five-letter word guess
        if len(guess) != 5:
            return JsonResponse({'message': 'Please enter a five-letter word.'})

        # Get Wordle word from session
        wordle_word = request.session['wordle_word']
        feedback = []

        # Check if guessed word matches
        if guess == wordle_word:
            request.session.flush()
            return JsonResponse({'result': 'Congratulations! You guessed the word!', 'success': True})

        # Check each letter in guess for match in Wordle word
        for i, char in enumerate(guess):
            if char == wordle_word[i]:
                feedback.append(f"{i+1} letter: right letter, right place!")
            elif char in wordle_word:
                feedback.append(f"{i+1} letter: right letter, wrong place.")

        # Decrement attempts
        request.session['attempts'] -= 1

        # Game over check
        if request.session['attempts'] <= 0:
            correct_word = request.session['wordle_word']
            request.session.flush()
            return JsonResponse({'result': f'Sorry, you ran out of attempts. The word was {correct_word}.', 'success': False})

        return JsonResponse({'result': feedback, 'remaining_attempts': request.session['attempts']})

    return render(request, 'wordle_app/index.html', {'attempts': request.session.get('attempts', 6)})
