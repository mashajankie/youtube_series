def log_op(operation, *args, **kwargs) -> None:
    """Log operations to a file."""
    details = ', '.join(map(str, args)) + ', '.join(f"{k}={v}" for k, v in kwargs.items())
    with open("./logs/logs.txt", "a") as log_file:
        log_file.write(f"{operation}: {details}\n")