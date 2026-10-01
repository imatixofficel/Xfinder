"""اجرای کامل pipeline."""
from .health_monitor import monitor
from .finder import collect
from .validator import validate
from .remixer import remix
from .publisher import publish

def main():
    monitor()
    collect()
    validate()
    remix()
    data=publish()
    print(data["stats"])

if __name__=="__main__": main()
