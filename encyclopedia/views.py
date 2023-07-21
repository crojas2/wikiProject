from django.shortcuts import render
from django.shortcuts import redirect
from django import forms

from . import util
import markdown2
import random as rand

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    page = util.get_entry(title)
    if (page):
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(util.get_entry(title))
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "message": "Not Found"
        })

def search(request):
    entries = util.list_entries()
    entries = [entry.lower() for entry in entries]

    query = request.GET.get("q", "")
    query = query.lower()

    
    if (query in entries):
        return redirect("entry", query)

    results = [entry for entry in entries if query in entry]
    return render(request, "encyclopedia/searchResults.html", {
        "entries": results
    })

def random(request):
    entries = util.list_entries()
    entry = rand.choice(entries)

    return render(request, "encyclopedia/entry.html", {
        "title": entry,
        "content": markdown2.markdown(util.get_entry(entry))
    })


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))


def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            if (util.get_entry(title)):
                return render(request, "encyclopedia/error.html", {
                    "title": title,
                    "message": "Already Exists"
                }) 
            else:
                util.save_entry(title, content)
                return redirect("entry", title)
        

    return render(request, "encyclopedia/newPage.html", {
            "form": NewEntryForm()
        })

class EditEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

def edit(request, title):
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect("entry", title)
            
    return render(request, "encyclopedia/editPage.html", {
            "title": title,
            "form": EditEntryForm(initial={"title": title, "content": util.get_entry(title)})
        })