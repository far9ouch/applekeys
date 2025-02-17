from flask import Flask, jsonify, render_template
from flask_cors import CORS
from apple_tv_bot import setup_driver, get_apple_tv_key
import threading
import queue
import time

app = Flask(__name__)
CORS(app)

# Queue to store generated keys
key_queue = queue.Queue(maxsize=10)
should_generate = True

def key_generator():
    global should_generate
    while should_generate:
        if key_queue.qsize() < 10:
            driver = None
            try:
                driver = setup_driver()
                key = get_apple_tv_key(driver)
                if key and not key_queue.full():
                    key_queue.put(key)
            except Exception as e:
                print(f"Error generating key: {str(e)}")
                time.sleep(5)  # Wait before retrying on error
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        else:
            time.sleep(1)  # Wait if queue is full

# Start key generator thread
generator_thread = threading.Thread(target=key_generator, daemon=True)
generator_thread.start()

def generate_single_key():
    driver = None
    try:
        driver = setup_driver()
        key = get_apple_tv_key(driver)
        return key
    except Exception as e:
        print(f"Error generating single key: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api_docs():
    return render_template('api.html')

@app.route('/test', methods=['GET'])
def test_api():
    return render_template('test.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "queue_size": key_queue.qsize()
    })

@app.route('/get-key', methods=['GET'])
def get_key():
    try:
        # First try to get from queue with a short timeout
        try:
            key = key_queue.get(timeout=1)
            return jsonify({
                "success": True,
                "key": key,
                "source": "queue"
            })
        except queue.Empty:
            # If queue is empty, generate a new key directly
            print("Queue empty, generating new key directly...")
            key = generate_single_key()
            if key:
                return jsonify({
                    "success": True,
                    "key": key,
                    "source": "direct"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to generate key. Please try again."
                }), 503
    except Exception as e:
        print(f"Error in get_key: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Server error. Please try again later."
        }), 500

@app.route('/queue-status', methods=['GET'])
def queue_status():
    return jsonify({
        "keys_available": key_queue.qsize(),
        "max_queue_size": 10
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 