from django.shortcuts import render
from django.http import HttpResponse
from http.client import HTTPResponse


# Create your views here.
def home(request):
    return HttpResponse("Welcome to Little Lemon")


def about(request):
    return HttpResponse("About Little Lemon")


def menu(request):
    return HttpResponse("Menu for Little Lemon")


def book(request):
    return HttpResponse("Book a table for Little Lemon")


def drinks(request, drink_name):
    drink = {
        "mocha": "type of coffee",
        "tea": "type of hot beverage",
        "lemonade": "type of hot refreshment",
    }
    choice_of_drink = drink[drink_name]
    return HttpResponse("<h2>{drink_name}<h2>" + choice_of_drink)
