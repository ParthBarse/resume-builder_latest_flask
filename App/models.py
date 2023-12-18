from flask import Flask, jsonify


class User:
    def signin(self):
        user = {
            "_id": "",
            "name": "",
            "email": "",
            "password": "",
        }
        return jsonify(user),200
