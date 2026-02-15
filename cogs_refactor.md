# Refactor (10.2.26)

Objective: Refactor the system into cogs. 

Key Questions: 
[] What will each cog be responsible for?
[] How will commands be defined? Will they host implementation logic? Or purely calling functions within each cog? 
    If we define some expectations for each function, it may be better for dragging and dropping changes.
[] What functions and objects will be in each cog? 
[] How will these objects and functions interact?

## Pure Functionality - View agnostics
pause, resume, seek, skip
view queue, remove from queue, enqueue
search: local, youtube
download: songs from yt
data: store songs on disk, manage all songs w/ database
statistics & analysis: commonly played, recommendations?
stream to voice channel
join, leave, move channel
song length limiting

## Subsystems

### Definitions
[file] Playback: (pause, resume, seek)
[file] Voice: (join, leave, move)
[file] Queue: (enqueue, dequeue, jump (to a new position in the queue), view_queue)
[file] Download: retrieves web-hosted audio files, or even from user messages to be stored on disk
[File] Data: CRUD operations on DB (CRUD songs, CRUD server information (important for paid service access))
[file] Search: search local_DB, access cached results, fuzzy match previous search results, cache DB requests

### [X] Playback
[X] pause
[X] resume

### [] Voice
[] move (allows bots to join and leave) - mask as join
[] leave
[] mute
[] volume

### Queue
[] enqueue
[] dequeue
[] jump

### Download
[] music download from youtube
[] music download from soundcloud
[] music download from spotify

(in the future, filter non-premium users, songs that are too long to download etc)
### Data
[] pull from API/local database


### Search
[] search youtube
[] search spotify
[] search soundcloud
[] general search (online and local)

<!-- ### Stream (future feature) -->
<!-- [] radio -->


## Cogs
## Commands
## Functions
