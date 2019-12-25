from processor import Processor

def main():
    controller = Processor()
    controller.update_new_tracks()
    controller.add_tracks_to_playlist()

if __name__ == '__main__':
    main()