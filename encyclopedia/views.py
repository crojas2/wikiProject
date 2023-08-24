from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django import forms
import markdown2
import random as rand

from . import util

def index(request):
    paginator = Paginator(util.list_entries(), 10)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    return render(request, "encyclopedia/index.html", {
        "entries": page_obj
    })

def entry(request, title):
    entry = util.get_entry(title)
    if (entry):
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