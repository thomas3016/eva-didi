import numpy as np
import os
import rosbag
import rospy
import sensor_msgs.point_cloud2 as pc2
import transform_points as tp
from velodyne_msgs.msg import VelodyneScan
from sensor_msgs.msg import PointCloud2

def process_pc2(msg):
    # CONVERT MESSAGE TO A NUMPY ARRAY OF POINT CLOUDS
    # creates a Nx5 array: [x, y, z, reflectance, ring]
    lidar = pc2.read_points(msg)
    lidar = np.array(list(lidar))
    print(msg.header.seq)
    birds_eye = tp.birds_eye_point_cloud(lidar, side_range=(-10, 10), fwd_range=(-10, 10), res=0.1)
    birds_eye.save('/data/output/birds_eye/' + str(msg.header.seq) + '.png')

class PointCloudProcessor:
    def __init__(self):
        rospy.init_node('PointCloudProcessor', anonymous=True)

    def add_subscriber(self, pc2_callback):
        rospy.Subscriber('/velodyne_points', PointCloud2, pc2_callback)

    def spin(self):
        rospy.spin()

    # Precondition: velodyne_pointcloud cloud_node is running.
    def read_bag(self, data_dir, bag_name, msg_count = None):
        bag_file = os.path.join(data_dir, bag_name)

        # Open rosbag.
        bag = rosbag.Bag(bag_file, "r")
        messages = bag.read_messages(topics=["/velodyne_packets"])
        n_lidar = bag.get_message_count(topic_filters=["/velodyne_packets"])

        # Publish velodyne packets from bag to topic.
        pub = rospy.Publisher('/velodyne_packets', VelodyneScan, queue_size=600)

        if msg_count is None:
            msg_count = n_lidar
        else:
            msg_count = min(msg_count, n_lidar)

        print('msg_count: ', msg_count)

        for i in range(msg_count):
            topic, msg, t = messages.next()
            pub.publish(msg)

processor = PointCloudProcessor()
processor.add_subscriber(process_pc2)

# Read rosbag.
data_dir = '/data/Didi-Release-2/Data/1'
bag_name = '2.bag'
processor.read_bag(data_dir, bag_name)

processor.spin()
