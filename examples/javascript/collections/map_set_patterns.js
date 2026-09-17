// Map and Set preserve value types and insertion order, unlike plain object keys.

const visits = [
  { userId: 7, page: "/home" },
  { userId: 3, page: "/pricing" },
  { userId: 7, page: "/docs" },
  { userId: 3, page: "/home" },
];

// Map is useful when keys are not necessarily strings.
const pagesByUser = new Map();
for (const { userId, page } of visits) {
  if (!pagesByUser.has(userId)) {
    pagesByUser.set(userId, []);
  }
  pagesByUser.get(userId).push(page);
}

// Set stores each value only once.
const uniquePages = new Set(visits.map((visit) => visit.page));

console.log("Grouped visits:");
for (const [userId, pages] of pagesByUser) {
  console.log(`User ${userId}: ${pages.join(", ")}`);
}

console.log("Unique pages:", [...uniquePages]);

// Object identity matters: two structurally equal objects are different keys.
const firstKey = { id: 1 };
const cache = new Map([[firstKey, "cached result"]]);
console.log("Same object:", cache.get(firstKey));
console.log("New look-alike object:", cache.get({ id: 1 })); // undefined

// Map and Set can be cloned without sharing their containers.
const copiedMap = new Map(pagesByUser);
const copiedSet = new Set(uniquePages);
console.log("Copied sizes:", copiedMap.size, copiedSet.size);
