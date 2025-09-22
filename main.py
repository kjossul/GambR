if __name__ == "__main__":

    import uvicorn
    # todo probably need to move to gunicorn and use --preload if we want multiple workers, due to using a scheduler
    # or we need to create different jobstores for each of the workers
    # a solution would be to use memory stores instead, and handle application crashes by checking predictions at startup
    uvicorn.run("app:app", reload=True)
