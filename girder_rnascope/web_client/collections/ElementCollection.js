import ElementCollection from '@girder/large_image_annotation/collections/ElementCollection';

ElementCollection.prototype.comparator = (a, b) => {
    a = a.get('label') || {};
    b = b.get('label') || {};
    if (Number(a.value) < Number(b.value)) {
        return -1;
    } else if (Number(a.value) > Number(b.value)) {
        return 1;
    }
    return 0;
};
