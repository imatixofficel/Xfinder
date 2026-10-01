"""اجرای pipeline محلی Xfinder."""
from health_monitor import main as health
from validator import main as validate
from publisher import main as publish

def main():
    health()
    validate()
    publish()
    print('Xfinder local pipeline completed.')

if __name__ == '__main__':
    main()
