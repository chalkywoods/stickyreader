# stickyreader

An automatic sticky note digitiser, created to speed up storage and sharing of ideas after group meetings and brainstorming sessions.

Stickyreader takes a photo of a board of sticky notes and converts them into a colour coded trello board.

Detection of sticky note location and colour uses a tuned tensorflow object detector, whilst handwriting recognition is processed in the Azure cloud. The Trello API is used to create and share the processed sticky notes.

A full write up of the demo is available on [the Valtech blog](https://www.valtech.com/insights/sticky-note-detection/).

Post It have now created a [similar system](https://www.3m.co.uk/3M/en_GB/post-it-notes/ideas/app/) themselves, though without handwriting detection.
