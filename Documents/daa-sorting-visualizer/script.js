const arrayContainer = document.getElementById("arrayContainer");
const algorithmSelect = document.getElementById("algorithm");
const sizeSlider = document.getElementById("size");
const speedSlider = document.getElementById("speed");
const sizeValue = document.getElementById("sizeValue");
const speedValue = document.getElementById("speedValue");
const generateBtn = document.getElementById("generateBtn");
const startBtn = document.getElementById("startBtn");

const algoName = document.getElementById("algoName");
const timeComplexity = document.getElementById("timeComplexity");
const spaceComplexity = document.getElementById("spaceComplexity");

let arr = [];
let isSorting = false;

const algorithmInfo = {
  bubble: {
    name: "Bubble Sort",
    time: "Best: O(n), Avg/Worst: O(n²)",
    space: "O(1)",
  },
  selection: {
    name: "Selection Sort",
    time: "Best/Avg/Worst: O(n²)",
    space: "O(1)",
  },
  insertion: {
    name: "Insertion Sort",
    time: "Best: O(n), Avg/Worst: O(n²)",
    space: "O(1)",
  },
  merge: {
    name: "Merge Sort",
    time: "Best/Avg/Worst: O(n log n)",
    space: "O(n)",
  },
  quick: {
    name: "Quick Sort",
    time: "Best/Avg: O(n log n), Worst: O(n²)",
    space: "O(log n)",
  },
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getDelay() {
  return Math.max(10, 520 - Number(speedSlider.value) * 5);
}

function updateInfo() {
  const info = algorithmInfo[algorithmSelect.value];
  algoName.textContent = info.name;
  timeComplexity.textContent = info.time;
  spaceComplexity.textContent = info.space;
}

function updateSliderLabels() {
  sizeValue.textContent = sizeSlider.value;
  speedValue.textContent = speedSlider.value;
}

function toggleControls(disabled) {
  algorithmSelect.disabled = disabled;
  sizeSlider.disabled = disabled;
  speedSlider.disabled = disabled;
  generateBtn.disabled = disabled;
  startBtn.disabled = disabled;
}

function generateArray(size = Number(sizeSlider.value)) {
  if (isSorting) return;

  arr = [];
  for (let i = 0; i < size; i++) {
    arr.push(Math.floor(Math.random() * 350) + 20);
  }
  renderArray();
}

function renderArray(active = [], compare = [], sorted = []) {
  arrayContainer.innerHTML = "";

  const activeSet = new Set(active);
  const compareSet = new Set(compare);
  const sortedSet = new Set(sorted);

  const maxVal = Math.max(...arr, 1);
  const width = Math.max(6, Math.floor(900 / arr.length) - 2);

  arr.forEach((value, index) => {
    const bar = document.createElement("div");
    bar.classList.add("bar");

    if (sortedSet.has(index)) {
      bar.classList.add("sorted");
    } else if (activeSet.has(index)) {
      bar.classList.add("active");
    } else if (compareSet.has(index)) {
      bar.classList.add("compare");
    }

    bar.style.height = `${(value / maxVal) * 100}%`;
    bar.style.width = `${width}px`;
    bar.title = value;

    if (arr.length <= 25) {
      const label = document.createElement("span");
      label.classList.add("bar-label");
      label.textContent = value;
      bar.appendChild(label);
    }

    arrayContainer.appendChild(bar);
  });
}

function getAllIndices() {
  return Array.from({ length: arr.length }, (_, i) => i);
}

function getRangeIndices(end) {
  return Array.from({ length: end + 1 }, (_, i) => i);
}

/* ---------------- Bubble Sort ---------------- */
async function bubbleSort() {
  const sorted = new Set();

  for (let i = 0; i < arr.length - 1; i++) {
    let swapped = false;

    for (let j = 0; j < arr.length - i - 1; j++) {
      renderArray([], [j, j + 1], Array.from(sorted));
      await sleep(getDelay());

      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        swapped = true;

        renderArray([j, j + 1], [], Array.from(sorted));
        await sleep(getDelay());
      }
    }

    sorted.add(arr.length - 1 - i);
    renderArray([], [], Array.from(sorted));
    await sleep(50);

    if (!swapped) {
      for (let k = 0; k < arr.length - 1 - i; k++) {
        sorted.add(k);
      }
      break;
    }
  }
}

/* ---------------- Selection Sort ---------------- */
async function selectionSort() {
  const sorted = new Set();

  for (let i = 0; i < arr.length; i++) {
    let minIndex = i;

    renderArray([minIndex], [], Array.from(sorted));
    await sleep(getDelay());

    for (let j = i + 1; j < arr.length; j++) {
      renderArray([minIndex], [j], Array.from(sorted));
      await sleep(getDelay());

      if (arr[j] < arr[minIndex]) {
        minIndex = j;
        renderArray([minIndex], [], Array.from(sorted));
        await sleep(getDelay());
      }
    }

    if (minIndex !== i) {
      [arr[i], arr[minIndex]] = [arr[minIndex], arr[i]];
      renderArray([i, minIndex], [], Array.from(sorted));
      await sleep(getDelay());
    }

    sorted.add(i);
    renderArray([], [], Array.from(sorted));
    await sleep(50);
  }
}

/* ---------------- Insertion Sort ---------------- */
async function insertionSort() {
  if (arr.length <= 1) return;

  renderArray([], [], [0]);
  await sleep(100);

  for (let i = 1; i < arr.length; i++) {
    let key = arr[i];
    let j = i - 1;

    renderArray([i], [], getRangeIndices(i - 1));
    await sleep(getDelay());

    while (j >= 0 && arr[j] > key) {
      renderArray([i], [j, j + 1], getRangeIndices(i - 1));
      await sleep(getDelay());

      arr[j + 1] = arr[j];
      renderArray([j, j + 1], [], getRangeIndices(i - 1));
      await sleep(getDelay());

      j--;
    }

    arr[j + 1] = key;
    renderArray([j + 1], [], getRangeIndices(i));
    await sleep(getDelay());
  }
}

/* ---------------- Merge Sort ---------------- */
async function mergeSort() {
  await mergeSortHelper(0, arr.length - 1);
}

async function mergeSortHelper(left, right) {
  if (left >= right) return;

  const mid = Math.floor((left + right) / 2);

  await mergeSortHelper(left, mid);
  await mergeSortHelper(mid + 1, right);
  await merge(left, mid, right);
}

async function merge(left, mid, right) {
  const leftPart = arr.slice(left, mid + 1);
  const rightPart = arr.slice(mid + 1, right + 1);

  let i = 0;
  let j = 0;
  let k = left;

  while (i < leftPart.length && j < rightPart.length) {
    renderArray([k], [left + i, mid + 1 + j], []);
    await sleep(getDelay());

    if (leftPart[i] <= rightPart[j]) {
      arr[k] = leftPart[i];
      i++;
    } else {
      arr[k] = rightPart[j];
      j++;
    }

    renderArray([k], [], []);
    await sleep(getDelay());
    k++;
  }

  while (i < leftPart.length) {
    arr[k] = leftPart[i];
    renderArray([k], [], []);
    await sleep(getDelay());
    i++;
    k++;
  }

  while (j < rightPart.length) {
    arr[k] = rightPart[j];
    renderArray([k], [], []);
    await sleep(getDelay());
    j++;
    k++;
  }
}

/* ---------------- Quick Sort ---------------- */
async function quickSort() {
  const fixed = new Set();
  await quickSortHelper(0, arr.length - 1, fixed);
}

async function quickSortHelper(low, high, fixed) {
  if (low > high) return;

  if (low === high) {
    fixed.add(low);
    renderArray([], [], Array.from(fixed));
    await sleep(40);
    return;
  }

  const pivotIndex = await partition(low, high, fixed);
  fixed.add(pivotIndex);

  renderArray([pivotIndex], [], Array.from(fixed));
  await sleep(getDelay());

  await quickSortHelper(low, pivotIndex - 1, fixed);
  await quickSortHelper(pivotIndex + 1, high, fixed);
}

async function partition(low, high, fixed) {
  const pivot = arr[high];
  let i = low - 1;

  for (let j = low; j < high; j++) {
    renderArray([high], [j], Array.from(fixed));
    await sleep(getDelay());

    if (arr[j] < pivot) {
      i++;
      [arr[i], arr[j]] = [arr[j], arr[i]];
      renderArray([i, j, high], [], Array.from(fixed));
      await sleep(getDelay());
    }
  }

  [arr[i + 1], arr[high]] = [arr[high], arr[i + 1]];
  renderArray([i + 1, high], [], Array.from(fixed));
  await sleep(getDelay());

  return i + 1;
}

/* ---------------- Start Sorting ---------------- */
async function startSorting() {
  if (isSorting) return;

  isSorting = true;
  toggleControls(true);

  try {
    const selectedAlgo = algorithmSelect.value;

    if (selectedAlgo === "bubble") {
      await bubbleSort();
    } else if (selectedAlgo === "selection") {
      await selectionSort();
    } else if (selectedAlgo === "insertion") {
      await insertionSort();
    } else if (selectedAlgo === "merge") {
      await mergeSort();
    } else if (selectedAlgo === "quick") {
      await quickSort();
    }

    renderArray([], [], getAllIndices());
  } catch (error) {
    console.error("Sorting error:", error);
  } finally {
    isSorting = false;
    toggleControls(false);
  }
}

/* ---------------- Event Listeners ---------------- */
algorithmSelect.addEventListener("change", updateInfo);

sizeSlider.addEventListener("input", () => {
  updateSliderLabels();
  generateArray(Number(sizeSlider.value));
});

speedSlider.addEventListener("input", updateSliderLabels);

generateBtn.addEventListener("click", () => {
  generateArray(Number(sizeSlider.value));
});

startBtn.addEventListener("click", startSorting);

/* ---------------- Initial Load ---------------- */
updateSliderLabels();
updateInfo();
generateArray();