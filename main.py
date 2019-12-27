from processor import Processor


def main():
    controller = Processor()
    print("Updating Best Of Playlist...")
    controller.update_best_of_playlist()
    print("Starting Explore Mode...")
    controller.start_explore_mode()


if __name__ == '__main__':
    main()
