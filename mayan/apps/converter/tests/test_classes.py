from __future__ import unicode_literals

from django.test import TestCase

from ..classes import (
    BaseTransformation, TransformationResize, TransformationRotate,
    TransformationZoom
)

TRANSFORMATION_RESIZE_WIDTH = 123
TRANSFORMATION_RESIZE_HEIGHT = 528
TRANSFORMATION_RESIZE_CACHE_HASH = '348d60cb7c028c95'
TRANSFORMATION_RESIZE_WIDTH_2 = 124
TRANSFORMATION_RESIZE_HEIGHT_2 = 529
TRANSFORMATION_RESIZE_CACHE_HASH_2 = '348d78cb5709c1bf'
TRANSFORMATION_ROTATE_DEGRESS = 34
TRANSFORMATION_ROTATE_CACHE_HASH = '45148f480ad5f8bd'
TRANSFORMATION_COMBINED_CACHE_HASH = '1267dbe78a1759da'
TRANSFORMATION_ZOOM_PERCENT = 49
TRANSFORMATION_ZOOM_CACHE_HASH = '1b333603674469e0'


class TransformationTestCase(TestCase):
    def test_cache_uniqness(self):
        transformation_1 = TransformationResize(width=640, height=640)

        transformation_2 = TransformationResize(width=800, height=800)

        self.assertNotEqual(
            transformation_1.cache_hash(), transformation_2.cache_hash()
        )

    def test_cache_combining_uniqness(self):
        transformation_1 = TransformationZoom(percent=100)
        transformation_2 = TransformationResize(width=800, height=800)

        self.assertNotEqual(
            BaseTransformation.combine((transformation_1, transformation_2)),
            BaseTransformation.combine((transformation_2, transformation_1)),
        )

    def test_resize_cache_hashing(self):
        # Test if the hash is being generated correctly
        transformation = TransformationResize(
            width=TRANSFORMATION_RESIZE_WIDTH,
            height=TRANSFORMATION_RESIZE_HEIGHT
        )

        self.assertEqual(
            transformation.cache_hash(), TRANSFORMATION_RESIZE_CACHE_HASH
        )

        # Test if the hash is being alternated correctly
        transformation = TransformationResize(
            width=TRANSFORMATION_RESIZE_WIDTH_2,
            height=TRANSFORMATION_RESIZE_HEIGHT_2
        )

        self.assertEqual(
            transformation.cache_hash(), TRANSFORMATION_RESIZE_CACHE_HASH_2
        )

    def test_rotate_cache_hashing(self):
        # Test if the hash is being generated correctly
        transformation = TransformationRotate(
            degrees=TRANSFORMATION_ROTATE_DEGRESS
        )

        self.assertEqual(
            transformation.cache_hash(), TRANSFORMATION_ROTATE_CACHE_HASH
        )

    def test_rotate_zoom_hashing(self):
        # Test if the hash is being generated correctly
        transformation = TransformationZoom(
            percent=TRANSFORMATION_ZOOM_PERCENT
        )

        self.assertEqual(
            transformation.cache_hash(), TRANSFORMATION_ZOOM_CACHE_HASH
        )

    def test_cache_hash_combining(self):
        # Test magic method and hash combining

        transformation_resize = TransformationResize(
            width=TRANSFORMATION_RESIZE_WIDTH,
            height=TRANSFORMATION_RESIZE_HEIGHT
        )

        transformation_rotate = TransformationRotate(
            degrees=TRANSFORMATION_ROTATE_DEGRESS
        )

        transformation_zoom = TransformationZoom(
            percent=TRANSFORMATION_ZOOM_PERCENT
        )

        self.assertEqual(
            BaseTransformation.combine(
                (transformation_rotate, transformation_resize, transformation_zoom)
            ), TRANSFORMATION_COMBINED_CACHE_HASH
        )
