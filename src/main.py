from CameraController import *
from ArduinoController import *
from GUI import *
from PS4Controller import *
from Scanner import *
from multiprocessing import Process, Queue


def launch_system_processes():
    queues = [Queue(0), Queue(0), Queue(0), Queue(0), Queue(0), Queue(0)]
    guiVideoQueue = Queue(0)
    guiLogQueue = Queue(0)
    processes = []

    processes.append(Process(target=launch_arduino_controller, args=(queues[2], queues[0], guiLogQueue,)))
    processes.append(Process(target=launch_camera, args=(queues[1], queues[0], guiVideoQueue, guiLogQueue,)))
    processes.append(Process(target=launch_gui, args=(queues[4], queues[0], guiVideoQueue, guiLogQueue,)))
    processes.append(Process(target=launch_ps4_controller, args=(queues[3], queues[0], guiLogQueue,)))
    processes.append(Process(target=launch_scanner, args=(queues[5], queues[0], guiLogQueue,)))

    for process in processes:
        process.start()
    return processes, queues


def terminate_system_processes(processes, queues):
    for queue in queues:
        queue.put([-1, -1, ['QUIT']])

    for process in processes:
        process.join()

    exit()


def main():
    processes, queues = launch_system_processes()
    while True:
        if not queues[0].empty():
            msg = queues[0].get()

            if msg[0] == -1:
                print("main: QUIT RECEIVED")
                terminate_system_processes(processes, queues)

            queues[msg[0]].put(msg)


if __name__ == '__main__':
    main()
