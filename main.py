if __name__ == "__main__":

    import uvicorn
    # todo probably need to move to gunicorn and use --preload if we want multiple workers
    # though I guess since we use a physical jobstore it shouldn't be an issue.
    uvicorn.run("app:app", reload=True)
