from processor import Processor


def main():
    controller = Processor()
    controller.update_new_tracks()
    controller.set_songs_to_bed_added()
    controller.update_new_playlist_tracks()
    controller.add_uris()
    controller.add_tracks_to_playlist()


if __name__ == '__main__':
    main()
